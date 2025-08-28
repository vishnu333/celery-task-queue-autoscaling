#!/usr/bin/env python3
"""
Celery Worker Script
Starts Celery workers and integrates with metrics collection
"""

import os
import sys
import time
import threading
from celery import Celery
from celery_app import app
from metrics import metrics

def start_metrics_server():
    """Start the metrics server in a separate thread"""
    from metrics import app as metrics_app
    metrics_app.run(host='0.0.0.0', port=8000, debug=False)

def main():
    """Main worker function"""
    print("Starting Celery Worker with Metrics Collection...")
    
    # Start metrics server in background thread
    metrics_thread = threading.Thread(target=start_metrics_server, daemon=True)
    metrics_thread.start()
    
    print("Metrics server started on port 8000")
    print("Worker starting...")
    
    # Start Celery worker
    argv = [
        'worker',
        '--loglevel=INFO',
        '--concurrency=2',  # Start with 2 worker processes
        '--hostname=worker@%h',
        '--queues=default',
        '--without-gossip',
        '--without-mingle',
        '--without-heartbeat'
    ]
    
    app.worker_main(argv)

if __name__ == '__main__':
    main()
