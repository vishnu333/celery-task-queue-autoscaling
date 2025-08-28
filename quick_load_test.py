#!/usr/bin/env python3
"""
Quick Load Test Simulation
Generates simulated metrics data quickly for visualization
"""

import time
import random
import json
from datetime import datetime

def quick_load_test():
    """Run a quick load test simulation"""
    print("🚀 Starting Quick Load Test Simulation...")
    
    metrics_data = []
    start_time = time.time()
    
    # Simulate 30 seconds of load testing (much faster!)
    duration_seconds = 30
    
    print(f"📊 Simulating {duration_seconds} seconds of load testing...")
    
    for second in range(duration_seconds):
        current_time = time.time()
        elapsed = current_time - start_time
        
        # Simulate different load patterns over 30 seconds
        if elapsed < 10:  # First 10 seconds: low load
            queue_depth = random.randint(1, 3)
            active_workers = 2
        elif elapsed < 20:  # 10-20 seconds: increasing load
            queue_depth = random.randint(3, 8)
            active_workers = 3
        else:  # 20-30 seconds: high load
            queue_depth = random.randint(8, 15)
            active_workers = 6
        
        # Add some randomness
        queue_depth += random.randint(-1, 1)
        queue_depth = max(0, queue_depth)
        
        # Simulate CPU and memory usage
        cpu_percent = min(100, 20 + (queue_depth * 3) + random.randint(-3, 3))
        memory_percent = min(100, 30 + (queue_depth * 2) + random.randint(-2, 2))
        
        # Create metrics entry
        metric_entry = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': elapsed,
            'queue_depth': queue_depth,
            'active_workers': active_workers,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'tasks_per_minute': queue_depth * 2 + random.randint(5, 15)
        }
        
        metrics_data.append(metric_entry)
        
        # Print progress every 5 seconds
        if second % 5 == 0:
            print(f"⏱️  {elapsed:.0f}s: Queue={queue_depth}, Workers={active_workers}, CPU={cpu_percent:.1f}%")
        
        time.sleep(0.1)  # Much faster - only 0.1 second delay
    
    print("✅ Quick load test completed!")
    return metrics_data

def save_metrics(metrics_data, filename='quick_load_test_metrics.json'):
    """Save metrics data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"💾 Metrics saved to {filename}")
    return filename

def create_plot_script(metrics_file):
    """Create a simple plotting script"""
    script_content = f'''#!/usr/bin/env python3
"""
Simple Metrics Plot
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Load data
with open('{metrics_file}', 'r') as f:
    data = json.load(f)

# Extract data
seconds = [m['elapsed_seconds'] for m in data]
queue_depth = [m['queue_depth'] for m in data]
workers = [m['active_workers'] for m in data]
cpu = [m['cpu_percent'] for m in data]
memory = [m['memory_percent'] for m in data]

# Create plot
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Celery Autoscaling - Load Test Results', fontsize=14, fontweight='bold')

# Queue Depth
ax1.plot(seconds, queue_depth, 'b-', linewidth=2, marker='o', markersize=4)
ax1.set_title('Queue Depth Over Time')
ax1.set_ylabel('Tasks in Queue')
ax1.set_xlabel('Time (seconds)')
ax1.grid(True, alpha=0.3)

# Active Workers
ax2.plot(seconds, workers, 'g-', linewidth=2, marker='s', markersize=4)
ax2.set_title('Worker Scaling')
ax2.set_ylabel('Number of Workers')
ax2.set_xlabel('Time (seconds)')
ax2.grid(True, alpha=0.3)

# Resource Usage
ax3.plot(seconds, cpu, 'r-', linewidth=2, label='CPU', marker='^', markersize=4)
ax3.plot(seconds, memory, 'orange', linewidth=2, label='Memory', marker='v', markersize=4)
ax3.set_title('Resource Utilization')
ax3.set_ylabel('Percentage (%)')
ax3.set_xlabel('Time (seconds)')
ax3.grid(True, alpha=0.3)
ax3.legend()

# Combined View
ax4.plot(seconds, queue_depth, 'b-', linewidth=2, label='Queue Depth')
ax4.plot(seconds, [w*2 for w in workers], 'g--', linewidth=2, label='Workers × 2')
ax4.set_title('Queue vs Workers')
ax4.set_ylabel('Count')
ax4.set_xlabel('Time (seconds)')
ax4.grid(True, alpha=0.3)
ax4.legend()

plt.tight_layout()
plt.savefig('autoscaling_graph.png', dpi=300, bbox_inches='tight')
plt.show()

print("📊 Graph saved as 'autoscaling_graph.png'")
print(f"📈 Peak Queue Depth: {max(queue_depth)}")
print(f"📈 Max Workers: {max(workers)}")
print(f"📈 Peak CPU: {max(cpu):.1f}%")
'''
    
    with open('plot_quick.py', 'w') as f:
        f.write(script_content)
    
    print("📝 Plot script created: plot_quick.py")

def main():
    """Main function"""
    print("🎯 Quick Load Test Simulation")
    print("=" * 40)
    
    # Run quick load test
    metrics_data = quick_load_test()
    
    # Save metrics
    metrics_file = save_metrics(metrics_data)
    
    # Create plot script
    create_plot_script(metrics_file)
    
    print("\n🚀 Next Steps:")
    print("1. Install matplotlib: pip install matplotlib")
    print("2. Run plot: python plot_quick.py")
    print("3. View graph: autoscaling_graph.png")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"   • Data points: {len(metrics_data)}")
    print(f"   • Duration: {metrics_data[-1]['elapsed_seconds']:.1f} seconds")
    print(f"   • Peak queue: {max(m['queue_depth'] for m in metrics_data)}")
    print(f"   • Max workers: {max(m['active_workers'] for m in metrics_data)}")

if __name__ == '__main__':
    main()
