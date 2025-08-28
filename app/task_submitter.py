#!/usr/bin/env python3
"""
Task Submission Script
Generates different task patterns to test autoscaling behavior
"""

import time
import random
import argparse
import math
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.celery_app import app, cpu_intensive_task, io_bound_task, mixed_task

def submit_gradual_increase(duration_minutes=10, max_tasks_per_minute=20):
    """Submit tasks with gradual increase in frequency"""
    print(f"Starting gradual increase pattern for {duration_minutes} minutes...")
    
    start_time = time.time()
    tasks_submitted = 0
    
    for minute in range(duration_minutes):
        # Calculate tasks for this minute (gradually increasing)
        tasks_this_minute = int((minute + 1) * max_tasks_per_minute / duration_minutes)
        
        print(f"Minute {minute + 1}: Submitting {tasks_this_minute} tasks")
        
        for _ in range(tasks_this_minute):
            # Randomly choose task type
            task_type = random.choice(['cpu', 'io', 'mixed'])
            
            if task_type == 'cpu':
                complexity = random.randint(500, 2000)
                task = cpu_intensive_task.delay(complexity=complexity)
            elif task_type == 'io':
                file_size = random.randint(512, 2048)
                task = io_bound_task.delay(file_size=file_size)
            else:
                cpu_comp = random.randint(300, 1000)
                io_size = random.randint(256, 1024)
                task = mixed_task.delay(cpu_complexity=cpu_comp, io_size=io_size)
            
            tasks_submitted += 1
            
            # Small delay between task submissions
            time.sleep(60 / tasks_this_minute)
        
        # Wait for next minute
        time.sleep(60)
    
    elapsed_time = time.time() - start_time
    print(f"Gradual increase completed: {tasks_submitted} tasks in {elapsed_time:.2f}s")

def submit_sudden_burst(burst_size=50, burst_count=3, delay_between_bursts=60):
    """Submit tasks in sudden bursts"""
    print(f"Starting sudden burst pattern: {burst_count} bursts of {burst_size} tasks each...")
    
    tasks_submitted = 0
    
    for burst in range(burst_count):
        print(f"Burst {burst + 1}: Submitting {burst_size} tasks rapidly...")
        
        burst_start = time.time()
        
        for i in range(burst_size):
            # Randomly choose task type
            task_type = random.choice(['cpu', 'io', 'mixed'])
            
            if task_type == 'cpu':
                complexity = random.randint(800, 2500)
                task = cpu_intensive_task.delay(complexity=complexity)
            elif task_type == 'io':
                file_size = random.randint(1024, 4096)
                task = io_bound_task.delay(file_size=file_size)
            else:
                cpu_comp = random.randint(600, 1500)
                io_size = random.randint(512, 2048)
                task = mixed_task.delay(cpu_complexity=cpu_comp, io_size=io_size)
            
            tasks_submitted += 1
            
            # Very small delay to prevent overwhelming
            time.sleep(0.1)
        
        burst_time = time.time() - burst_start
        print(f"Burst {burst + 1} completed in {burst_time:.2f}s")
        
        if burst < burst_count - 1:
            print(f"Waiting {delay_between_bursts}s before next burst...")
            time.sleep(delay_between_bursts)
    
    print(f"Sudden burst completed: {tasks_submitted} tasks total")

def submit_oscillating(duration_minutes=15, base_tasks_per_minute=10, amplitude=15):
    """Submit tasks in oscillating pattern (sine wave)"""
    print(f"Starting oscillating pattern for {duration_minutes} minutes...")
    
    start_time = time.time()
    tasks_submitted = 0
    
    for minute in range(duration_minutes):
        # Calculate tasks using sine wave pattern
        # This creates a smooth oscillation between low and high task rates
        oscillation = math.sin(2 * math.pi * minute / (duration_minutes / 2))
        tasks_this_minute = int(base_tasks_per_minute + amplitude * oscillation)
        
        # Ensure we don't have negative tasks
        tasks_this_minute = max(1, tasks_this_minute)
        
        print(f"Minute {minute + 1}: Submitting {tasks_this_minute} tasks (oscillation: {oscillation:.2f})")
        
        for _ in range(tasks_this_minute):
            # Randomly choose task type
            task_type = random.choice(['cpu', 'io', 'mixed'])
            
            if task_type == 'cpu':
                complexity = random.randint(600, 1800)
                task = cpu_intensive_task.delay(complexity=complexity)
            elif task_type == 'io':
                file_size = random.randint(768, 1536)
                task = io_bound_task.delay(file_size=file_size)
            else:
                cpu_comp = random.randint(400, 1200)
                io_size = random.randint(384, 1280)
                task = mixed_task.delay(cpu_complexity=cpu_comp, io_size=io_size)
            
            tasks_submitted += 1
            
            # Small delay between task submissions
            time.sleep(60 / tasks_this_minute)
        
        # Wait for next minute
        time.sleep(60)
    
    elapsed_time = time.time() - start_time
    print(f"Oscillating pattern completed: {tasks_submitted} tasks in {elapsed_time:.2f}s")

def main():
    parser = argparse.ArgumentParser(description='Submit tasks to test autoscaling')
    parser.add_argument('--pattern', choices=['gradual', 'burst', 'oscillating'], 
                       default='gradual', help='Task submission pattern')
    parser.add_argument('--duration', type=int, default=10, 
                       help='Duration in minutes for gradual/oscillating patterns')
    parser.add_argument('--burst-size', type=int, default=50, 
                       help='Number of tasks per burst')
    parser.add_argument('--burst-count', type=int, default=3, 
                       help='Number of bursts')
    
    args = parser.parse_args()
    
    print("Task Submitter for Celery Autoscaling Test")
    print("=" * 50)
    
    if args.pattern == 'gradual':
        submit_gradual_increase(args.duration)
    elif args.pattern == 'burst':
        submit_sudden_burst(args.burst_size, args.burst_count)
    elif args.pattern == 'oscillating':
        submit_oscillating(args.duration)
    
    print("Task submission completed!")

if __name__ == '__main__':
    main()
