# Installation Guide - Celery Task Queue Autoscaling System

## Prerequisites Installation

### 1. Docker Desktop
**macOS:**
```bash
# Install via Homebrew
brew install --cask docker

# Or download from https://www.docker.com/products/docker-desktop
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop
- Install and restart your system

### 2. Minikube
**macOS:**
```bash
# Install via Homebrew
brew install minikube

# Or download binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube
```

**Linux:**
```bash
# Download binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Windows:**
```bash
# Using Chocolatey
choco install minikube

# Or download binary from https://minikube.sigs.k8s.io/docs/start/
```

### 3. kubectl
**macOS:**
```bash
# Install via Homebrew
brew install kubectl

# Or download binary
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

**Linux:**
```bash
# Download binary
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

**Windows:**
```bash
# Using Chocolatey
choco install kubernetes-cli

# Or download from https://kubernetes.io/docs/tasks/tools/install-kubectl/
```

### 4. Python 3.11+
**macOS:**
```bash
# Install via Homebrew
brew install python@3.11

# Or download from https://www.python.org/downloads/
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-pip

# CentOS/RHEL
sudo yum install python3.11 python3.11-pip
```

**Windows:**
- Download from https://www.python.org/downloads/
- Ensure "Add Python to PATH" is checked during installation

## System Setup

### 1. Clone Repository
```bash
git clone https://github.com/vishnu333/celery-task-queue-autoscaling.git
cd celery-task-queue-autoscaling
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Setup
```bash
python test_setup.py
```

## Minikube Setup

### 1. Start Minikube
```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons
minikube addons enable metrics-server
```

### 2. Verify Minikube Status
```bash
minikube status
kubectl get nodes
```

### 3. Set Docker Environment
```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)
```

## Deployment

### 1. Automated Deployment
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 2. Manual Deployment
```bash
# Build Docker images
docker build -t celery-autoscaling:latest .
docker build -f Dockerfile.metrics-adapter -t custom-metrics-adapter:latest .

# Deploy components
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/celery-worker-deployment.yaml
kubectl apply -f k8s/custom-metrics-adapter.yaml
kubectl apply -f k8s/hpa.yaml
```

### 3. Verify Deployment
```bash
# Check pod status
kubectl get pods

# Check services
kubectl get services

# Check HPA
kubectl get hpa
```

## Testing

### 1. Test Task Generation
```bash
# Activate virtual environment
source venv/bin/activate

# Test gradual increase pattern
python app/task_submitter.py --pattern gradual --duration 10

# Test sudden burst pattern
python app/task_submitter.py --pattern burst --burst-size 50 --burst-count 3

# Test oscillating pattern
python app/task_submitter.py --pattern oscillating --duration 15
```

### 2. Monitor System
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

#### 1. Minikube Won't Start
```bash
# Check system resources
minikube start --cpus=2 --memory=4096 --disk-size=10g

# Reset if needed
minikube delete
minikube start --cpus=4 --memory=8192 --disk-size=20g
```

#### 2. Docker Build Fails
```bash
# Ensure Docker is running
docker ps

# Check Minikube Docker environment
eval $(minikube docker-env)
docker ps
```

#### 3. Pods Not Starting
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check resource availability
kubectl describe node
```

#### 4. HPA Not Scaling
```bash
# Check HPA status
kubectl describe hpa celery-worker-hpa

# Check custom metrics
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/default/services/celery-worker-service/queue_depth"

# Check metrics adapter logs
kubectl logs deployment/custom-metrics-adapter
```

### Debug Commands
```bash
# Check system status
kubectl get all
kubectl get events --sort-by='.lastTimestamp'

# Test service connectivity
kubectl run test-pod --image=busybox --rm -it --restart=Never -- wget -O- http://celery-worker-service:8000/health

# Check resource usage
kubectl top pods
kubectl top nodes
```

## Performance Tuning

### 1. Resource Limits
Adjust resource limits in Kubernetes manifests based on your system:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 2. HPA Configuration
Modify HPA settings in `k8s/hpa.yaml`:
```yaml
minReplicas: 2
maxReplicas: 10
targetAverageValue: 5  # Queue depth per worker
```

### 3. Scaling Behavior
Adjust scaling policies for your workload:
```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 60
  scaleDown:
    stabilizationWindowSeconds: 300
```

## Next Steps

After successful deployment:

1. **Monitor Performance**: Use the provided monitoring commands
2. **Test Load Patterns**: Run different task generation scenarios
3. **Analyze Results**: Review the performance analysis report
4. **Optimize Settings**: Adjust HPA and resource configurations
5. **Scale Up**: Consider production deployment with proper monitoring

## Support

- **Repository**: https://github.com/vishnu333/celery-task-queue-autoscaling
- **Issues**: Create GitHub issues for bugs or questions
- **Documentation**: Refer to README.md and ANALYSIS_REPORT.md

---

**This installation guide ensures you have all prerequisites and can successfully deploy and test the Celery Task Queue Autoscaling System.**
