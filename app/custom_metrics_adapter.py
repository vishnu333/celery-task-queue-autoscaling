#!/usr/bin/env python3
"""
Custom Metrics Adapter for Kubernetes HPA
Exposes queue depth metrics to Kubernetes for autoscaling decisions
"""

import os
import time
import requests
import json
from flask import Flask, jsonify, request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Configuration
CELERY_SERVICE_URL = os.getenv('CELERY_SERVICE_URL', 'http://celery-worker-service:8000')
METRICS_PORT = int(os.getenv('METRICS_PORT', 8080))

class CustomMetricsAdapter:
    def __init__(self):
        self.last_queue_depth = 0
        self.last_update = 0
        self.update_interval = 5  # Update every 5 seconds
        
    def get_queue_depth(self):
        """Get queue depth from Celery service"""
        current_time = time.time()
        
        # Only update if enough time has passed
        if current_time - self.last_update >= self.update_interval:
            try:
                response = requests.get(f"{CELERY_SERVICE_URL}/queue-depth", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.last_queue_depth = data.get('queue_depth', 0)
                    self.last_update = current_time
                else:
                    print(f"Error getting queue depth: {response.status_code}")
            except Exception as e:
                print(f"Exception getting queue depth: {e}")
        
        return self.last_queue_depth

# Global adapter instance
adapter = CustomMetricsAdapter()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/ready')
def ready():
    """Readiness check endpoint"""
    try:
        # Check if we can reach the Celery service
        response = requests.get(f"{CELERY_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({'status': 'ready'})
        else:
            return jsonify({'status': 'not ready'}), 503
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/apis/custom.metrics.k8s.io/v1beta1/namespaces/<namespace>/services/<service_name>/queue_depth')
def custom_metrics(namespace, service_name):
    """Custom metrics endpoint for Kubernetes HPA"""
    queue_depth = adapter.get_queue_depth()
    
    # Return in Kubernetes custom metrics format
    return jsonify({
        "kind": "MetricValueList",
        "apiVersion": "custom.metrics.k8s.io/v1beta1",
        "metadata": {
            "selfLink": f"/apis/custom.metrics.k8s.io/v1beta1/namespaces/{namespace}/services/{service_name}/queue_depth"
        },
        "items": [
            {
                "describedObject": {
                    "kind": "Service",
                    "name": service_name,
                    "apiVersion": "v1"
                },
                "metricName": "queue_depth",
                "timestamp": time.time(),
                "value": queue_depth
            }
        ]
    })

@app.route('/apis/custom.metrics.k8s.io/v1beta1/namespaces/<namespace>/pods/*/queue_depth')
def pod_metrics(namespace):
    """Pod-level metrics endpoint"""
    queue_depth = adapter.get_queue_depth()
    
    return jsonify({
        "kind": "MetricValueList",
        "apiVersion": "custom.metrics.k8s.io/v1beta1",
        "metadata": {
            "selfLink": f"/apis/custom.metrics.k8s.io/v1beta1/namespaces/{namespace}/pods/*/queue_depth"
        },
        "items": [
            {
                "describedObject": {
                    "kind": "Pod",
                    "name": "*",
                    "apiVersion": "v1"
                },
                "metricName": "queue_depth",
                "timestamp": time.time(),
                "value": queue_depth
            }
        ]
    })

@app.route('/apis/custom.metrics.k8s.io/v1beta1/namespaces/<namespace>/deployments/*/queue_depth')
def deployment_metrics(namespace):
    """Deployment-level metrics endpoint"""
    queue_depth = adapter.get_queue_depth()
    
    return jsonify({
        "kind": "MetricValueList",
        "apiVersion": "custom.metrics.k8s.io/v1beta1",
        "metadata": {
            "selfLink": f"/apis/custom.metrics.k8s.io/v1beta1/namespaces/{namespace}/deployments/*/queue_depth"
        },
        "items": [
            {
                "describedObject": {
                    "kind": "Deployment",
                    "name": "*",
                    "apiVersion": "apps/v1"
                },
                "metricName": "queue_depth",
                "timestamp": time.time(),
                "value": queue_depth
            }
        ]
    })

if __name__ == '__main__':
    print(f"Starting Custom Metrics Adapter on port {METRICS_PORT}")
    print(f"Celery service URL: {CELERY_SERVICE_URL}")
    app.run(host='0.0.0.0', port=METRICS_PORT, debug=False)
