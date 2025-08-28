#!/bin/bash

echo "🚀 Celery Task Queue Autoscaling System - Deployment Script"
echo "=========================================================="

# Check if Minikube is running
if ! minikube status | grep -q "Running"; then
    echo "Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --disk-size=20g
else
    echo "Minikube is already running"
fi

# Enable addons
echo "Enabling Minikube addons..."
minikube addons enable metrics-server

# Set Docker environment to use Minikube's Docker daemon
eval $(minikube docker-env)

echo "Building Docker images..."
# Build Celery worker image
docker build -t celery-autoscaling:latest .

# Build custom metrics adapter image
docker build -f Dockerfile.metrics-adapter -t custom-metrics-adapter:latest .

echo "Deploying to Kubernetes..."
# Apply Redis deployment
kubectl apply -f k8s/redis-deployment.yaml

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/redis

# Apply Celery worker deployment
kubectl apply -f k8s/celery-worker-deployment.yaml

# Wait for Celery workers to be ready
echo "Waiting for Celery workers to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/celery-worker

# Apply custom metrics adapter
kubectl apply -f k8s/custom-metrics-adapter.yaml

# Wait for metrics adapter to be ready
echo "Waiting for custom metrics adapter to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/custom-metrics-adapter

# Apply HPA
kubectl apply -f k8s/hpa.yaml

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 System Status:"
kubectl get pods
echo ""
echo "🔗 Services:"
kubectl get services
echo ""
echo "📈 HPA Status:"
kubectl get hpa
echo ""
echo "🌐 Access Points:"
echo "Minikube IP: $(minikube ip)"
echo "Celery Worker Service: $(minikube ip):$(kubectl get service celery-worker-service -o jsonpath='{.spec.ports[0].nodePort}')"
echo ""
echo "📝 Next Steps:"
echo "1. Run task generation scripts to test autoscaling"
echo "2. Monitor HPA behavior: kubectl get hpa -w"
echo "3. Check pod scaling: kubectl get pods -w"
echo "4. View metrics: kubectl port-forward service/celery-worker-service 8000:8000"
