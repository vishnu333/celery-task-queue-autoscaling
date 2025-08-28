#!/usr/bin/env python3
"""
Simple Metrics Plot
"""

import json
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Load data
with open('quick_load_test_metrics.json', 'r') as f:
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
