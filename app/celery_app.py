from celery import Celery
import time
import os
import random
import math
from celery.utils.log import get_task_logger

# Configure Celery
app = Celery('autoscaling_demo')

# Redis broker configuration
app.conf.update(
    broker_url='redis://redis-service:6379/0',
    result_backend='redis://redis-service:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
)

logger = get_task_logger(__name__)

@app.task(bind=True, name='tasks.cpu_intensive')
def cpu_intensive_task(self, complexity=1000):
    """
    CPU-intensive task that simulates heavy computation
    """
    logger.info(f"Starting CPU-intensive task {self.request.id} with complexity {complexity}")
    
    start_time = time.time()
    
    # Simulate CPU-intensive work
    result = 0
    for i in range(complexity):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
        if i % 100 == 0:
            # Update task state
            self.update_state(
                state='PROGRESS',
                meta={'current': i, 'total': complexity, 'result': result}
            )
    
    processing_time = time.time() - start_time
    logger.info(f"CPU-intensive task {self.request.id} completed in {processing_time:.2f}s")
    
    return {
        'task_id': self.request.id,
        'type': 'cpu_intensive',
        'complexity': complexity,
        'processing_time': processing_time,
        'result': result
    }

@app.task(bind=True, name='tasks.io_bound')
def io_bound_task(self, file_size=1024):
    """
    I/O-bound task that simulates file operations
    """
    logger.info(f"Starting I/O-bound task {self.request.id} with file_size {file_size}")
    
    start_time = time.time()
    
    # Simulate I/O operations
    temp_file = f"/tmp/task_{self.request.id}.tmp"
    
    # Simulate file write
    with open(temp_file, 'w') as f:
        for i in range(file_size):
            f.write(f"Line {i}: Some data for task {self.request.id}\n")
            if i % 100 == 0:
                self.update_state(
                    state='PROGRESS',
                    meta={'current': i, 'total': file_size, 'operation': 'writing'}
                )
    
    # Simulate file read
    with open(temp_file, 'r') as f:
        lines = f.readlines()
    
    # Cleanup
    os.remove(temp_file)
    
    processing_time = time.time() - start_time
    logger.info(f"I/O-bound task {self.request.id} completed in {processing_time:.2f}s")
    
    return {
        'task_id': self.request.id,
        'type': 'io_bound',
        'file_size': file_size,
        'processing_time': processing_time,
        'lines_processed': len(lines)
    }

@app.task(bind=True, name='tasks.mixed_task')
def mixed_task(self, cpu_complexity=500, io_size=512):
    """
    Mixed task that combines both CPU and I/O operations
    """
    logger.info(f"Starting mixed task {self.request.id}")
    
    start_time = time.time()
    
    # CPU-intensive part
    result = 0
    for i in range(cpu_complexity):
        result += math.sqrt(i) * math.sin(i)
    
    # I/O part
    temp_file = f"/tmp/mixed_task_{self.request.id}.tmp"
    with open(temp_file, 'w') as f:
        for i in range(io_size):
            f.write(f"Mixed task data {i}: {result}\n")
    
    with open(temp_file, 'r') as f:
        lines = f.readlines()
    
    os.remove(temp_file)
    
    processing_time = time.time() - start_time
    logger.info(f"Mixed task {self.request.id} completed in {processing_time:.2f}s")
    
    return {
        'task_id': self.request.id,
        'type': 'mixed',
        'cpu_complexity': cpu_complexity,
        'io_size': io_size,
        'processing_time': processing_time,
        'result': result,
        'lines_processed': len(lines)
    }

if __name__ == '__main__':
    app.start()
