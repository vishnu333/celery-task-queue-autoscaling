import time
import psutil
import redis
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Flask, Response
import json

# Prometheus metrics
TASK_COUNTER = Counter('celery_tasks_total', 'Total number of tasks', ['task_type', 'status'])
TASK_DURATION = Histogram('celery_task_duration_seconds', 'Task duration in seconds', ['task_type'])
QUEUE_DEPTH = Gauge('celery_queue_depth', 'Number of tasks in queue')
WORKER_CPU_USAGE = Gauge('celery_worker_cpu_percent', 'Worker CPU usage percentage')
WORKER_MEMORY_USAGE = Gauge('celery_worker_memory_bytes', 'Worker memory usage in bytes')
ACTIVE_WORKERS = Gauge('celery_active_workers', 'Number of active workers')

class CeleryMetrics:
    def __init__(self, redis_host='redis-service', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.last_update = 0
        self.update_interval = 5  # Update metrics every 5 seconds
        
    def get_queue_depth(self):
        """Get the current queue depth from Redis"""
        try:
            # Get active, reserved, and scheduled tasks
            active = len(self.redis_client.smembers('celery:active'))
            reserved = len(self.redis_client.smembers('celery:reserved'))
            scheduled = len(self.redis_client.zrange('celery:scheduled', 0, -1))
            
            total_depth = active + reserved + scheduled
            QUEUE_DEPTH.set(total_depth)
            return total_depth
        except Exception as e:
            print(f"Error getting queue depth: {e}")
            return 0
    
    def get_worker_stats(self):
        """Get worker statistics"""
        try:
            # Get worker information from Redis
            workers = self.redis_client.smembers('celery:workers')
            active_workers = len(workers)
            ACTIVE_WORKERS.set(active_workers)
            
            # Get system resource usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            WORKER_CPU_USAGE.set(cpu_percent)
            WORKER_MEMORY_USAGE.set(memory.used)
            
            return {
                'active_workers': active_workers,
                'cpu_percent': cpu_percent,
                'memory_used': memory.used,
                'memory_percent': memory.percent
            }
        except Exception as e:
            print(f"Error getting worker stats: {e}")
            return {'active_workers': 0, 'cpu_percent': 0, 'memory_used': 0, 'memory_percent': 0}
    
    def record_task_completion(self, task_type, duration, status='completed'):
        """Record task completion metrics"""
        TASK_COUNTER.labels(task_type=task_type, status=status).inc()
        TASK_DURATION.labels(task_type=task_type).observe(duration)
    
    def get_metrics_summary(self):
        """Get a summary of all metrics for autoscaling decisions"""
        current_time = time.time()
        
        # Only update if enough time has passed
        if current_time - self.last_update >= self.update_interval:
            queue_depth = self.get_queue_depth()
            worker_stats = self.get_worker_stats()
            self.last_update = current_time
            
            return {
                'queue_depth': queue_depth,
                'active_workers': worker_stats['active_workers'],
                'cpu_percent': worker_stats['cpu_percent'],
                'memory_percent': worker_stats['memory_percent'],
                'timestamp': current_time
            }
        else:
            # Return cached metrics
            return {
                'queue_depth': QUEUE_DEPTH._value.get(),
                'active_workers': ACTIVE_WORKERS._value.get(),
                'cpu_percent': WORKER_CPU_USAGE._value.get(),
                'memory_percent': WORKER_MEMORY_USAGE._value.get(),
                'timestamp': self.last_update
            }

# Global metrics instance
metrics = CeleryMetrics()

# Flask app for metrics endpoint
app = Flask(__name__)

@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        queue_depth = metrics.get_queue_depth()
        worker_stats = metrics.get_worker_stats()
        
        return {
            'status': 'healthy',
            'queue_depth': queue_depth,
            'worker_stats': worker_stats,
            'timestamp': time.time()
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

@app.route('/queue-depth')
def queue_depth_endpoint():
    """Simple queue depth endpoint for autoscaling"""
    try:
        depth = metrics.get_queue_depth()
        return {'queue_depth': depth, 'timestamp': time.time()}
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
