# Installation Guide - macOS

## Prerequisites

### Install Required Tools

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker

# Install Minikube
brew install minikube

# Install kubectl
brew install kubectl

# Install Python 3.11+
brew install python@3.11
```

### Verify Installations

```bash
docker --version
minikube version
kubectl version --client
python3 --version
```

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/vishnu333/celery-task-queue-autoscaling.git
cd celery-task-queue-autoscaling
```

### 2. Create Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Minikube

```bash
minikube start --cpus=4 --memory=7000 --disk-size=20g
minikube addons enable metrics-server
eval $(minikube docker-env)
```

### 4. Deploy System

```bash
chmod +x deploy.sh
./deploy.sh
```

## Testing

### Verify Deployment

```bash
kubectl get pods
kubectl get services
kubectl get hpa
```

### Test Task Generation

```bash
# Activate virtual environment
source venv/bin/activate

# Test gradual increase pattern
python app/task_submitter.py --pattern gradual --duration 5

# Test sudden burst pattern
python app/task_submitter.py --pattern burst --burst-size 20 --burst-count 2

# Test oscillating pattern
python app/task_submitter.py --pattern oscillating --duration 10
```

### Monitor System

```bash
# Watch HPA behavior
kubectl get hpa -w

# Monitor pod scaling
kubectl get pods -w

# Check metrics
kubectl port-forward service/celery-worker-service 8000:8000
curl http://localhost:8000/metrics
```

## Troubleshooting

### Common Issues

**Minikube won't start**
```bash
minikube delete
minikube start --cpus=4 --memory=7000 --disk-size=20g
```

**Docker build fails**
```bash
# Restart Docker Desktop
# Or try building with different base image
docker build -f Dockerfile.alternative .
```

**Pods not starting**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Alternative Setup

If you encounter Docker network issues:

1. **Test locally first**:
   ```bash
   source venv/bin/activate
   python app/worker.py
   ```

2. **Use existing images**:
   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   ```

3. **Check system status**:
   ```bash
   python verify_system.py
   ```

## Quick Commands

```bash
# Start everything
minikube start
./deploy.sh

# Check status
kubectl get all
kubectl get hpa

# Test locally
source venv/bin/activate
python app/task_submitter.py --pattern gradual --duration 5

# Clean up
minikube delete
```

## Support

- **Repository**: https://github.com/vishnu333/celery-task-queue-autoscaling
- **Documentation**: README.md, ANALYSIS_REPORT.md
- **Issues**: Create GitHub issues for problems

---

**This guide covers the essential steps to get the Celery Task Queue Autoscaling System running on macOS.**
