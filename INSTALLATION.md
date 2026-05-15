# Installation and Setup Guide

## Prerequisites

### System Requirements
- Python 3.11 or higher
- Docker and Docker Buildx (for containerization)
- Kubernetes 1.24+ (for deployment)
- 4GB+ RAM for model inference
- 10GB+ disk space for models

### Required Services
- Kubernetes cluster with API access
- (Optional) MLFlow tracking server
- (Optional) Slack workspace with webhook

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourorg/k8s-ai-incident-rca-assistant.git
cd k8s-ai-incident-rca-assistant
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n k8s-rca python=3.11
conda activate k8s-rca
```

### 3. Install Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# For development (includes testing tools)
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov black flake8 pylint
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
# - KUBECONFIG: path to your kubeconfig file
# - MLFLOW_TRACKING_URI: MLFlow server URL
# - SLACK_WEBHOOK_URL: Slack webhook for notifications
```

### 5. Verify Kubernetes Access
```bash
# Test kubectl access
kubectl get nodes
kubectl get pods --all-namespaces

# Verify kubeconfig in project
export KUBECONFIG=$(pwd)/kubeconfig
# Copy your kubeconfig or set KUBECONFIG in .env
```

### 6. Run Locally
```bash
# Development mode (with hot reload)
python dev.py

# Production mode
python main.py
```

### 7. Test the API
```bash
# Health check
curl http://localhost:8000/health

# List incidents
curl http://localhost:8000/api/v1/incidents

# Create incident
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "pod_name": "test-pod",
    "namespace": "default",
    "error_message": "Test incident",
    "severity": "high"
  }'
```

## Docker Setup

### Build Docker Image
```bash
# Build locally
docker build -t k8s-incident-rca:latest .

# Build with Buildx (cross-platform)
docker buildx build --platform linux/amd64,linux/arm64 \
  -t k8s-incident-rca:latest \
  --push .
```

### Run with Docker Compose
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Run Docker Container
```bash
# Basic run
docker run -p 8000:8000 k8s-incident-rca:latest

# With Kubernetes config
docker run -p 8000:8000 \
  -v ~/.kube/config:/app/.kube/config \
  k8s-incident-rca:latest

# With environment file
docker run --env-file .env -p 8000:8000 k8s-incident-rca:latest
```

## Kubernetes Deployment

### Prerequisites
- kubectl configured with cluster access
- Docker image pushed to container registry
- Kubernetes namespace created

### Create Namespace (Optional)
```bash
kubectl create namespace k8s-rca
```

### Apply Kubernetes Manifests
```bash
# Apply all resources
kubectl apply -f kubernetes/

# Verify deployment
kubectl get deployment k8s-incident-rca
kubectl get pods -l app=k8s-incident-rca
kubectl get svc k8s-incident-rca

# Check logs
kubectl logs -f deployment/k8s-incident-rca
```

### Create Secrets
```bash
# Create Slack webhook secret
kubectl create secret generic k8s-incident-rca-secrets \
  --from-literal=slack_webhook_url=https://hooks.slack.com/...

# Create Docker registry secret (if needed)
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=username \
  --docker-password=token \
  --docker-email=email@example.com
```

### Access the Service
```bash
# Port forward to local
kubectl port-forward svc/k8s-incident-rca 8000:80

# Or use ingress (configure Ingress resource)
# https://k8s-rca.example.com
```

## Development Workflow

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app/ --cov-report=html

# Run specific test file
pytest tests/test_rag.py -v

# Run specific test
pytest tests/test_rag.py::TestRAGRetriever::test_retriever_initialization -v
```

### Code Quality Checks
```bash
# Linting
flake8 app/
pylint app/

# Code formatting
black app/
black --check app/

# Import sorting
isort app/
isort --check-only app/

# Type checking
mypy app/ --ignore-missing-imports
```

### Running Examples
```bash
# Run example code
python examples.py
```

## Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| LOG_LEVEL | Python logging level | INFO |
| KUBECONFIG | Path to kubeconfig file | ~/.kube/config |
| IN_CLUSTER | Running in K8s cluster | false |
| EMBEDDING_MODEL | Sentence transformer model | all-MiniLM-L6-v2 |
| MLFLOW_TRACKING_URI | MLFlow server URI | http://localhost:5000 |
| SLACK_WEBHOOK_URL | Slack webhook URL | (optional) |
| API_HOST | API host address | 0.0.0.0 |
| API_PORT | API port number | 8000 |

### Kubernetes Helm Values (Optional)
```yaml
replicaCount: 2
image:
  repository: ghcr.io/yourorg/k8s-incident-rca
  tag: latest
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
mlflow:
  uri: "http://mlflow:5000"
slack:
  webhookUrl: ""
```

## Troubleshooting

### Cannot Connect to Kubernetes API
```bash
# Check kubeconfig
kubectl cluster-info
kubectl auth can-i get pods

# Verify in Python
from kubernetes import client, config
config.load_kube_config()
v1 = client.CoreV1Api()
print(v1.get_api_resources())
```

### Memory Issues
```bash
# Reduce embedding model size
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Use quantized LLM models
HUGGINGFACE_MODEL=distilgpt2

# Monitor memory usage
docker stats k8s-incident-rca
```

### Model Download Issues
```bash
# Pre-download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Set model cache directory
export HF_HOME=/data/models
```

## Performance Tuning

### For Development
```bash
# Use smaller models for faster startup
EMBEDDING_MODEL=all-MiniLM-L6-v2
HUGGINGFACE_MODEL=distilgpt2
```

### For Production
```bash
# Use larger models for better accuracy
EMBEDDING_MODEL=all-mpnet-base-v2
HUGGINGFACE_MODEL=gpt2-medium

# Increase resources
kubectl set resources deployment k8s-incident-rca \
  --limits=cpu=2,memory=2Gi \
  --requests=cpu=1,memory=1Gi
```

## Next Steps

1. **Configure Integrations**
   - Set up Slack webhook
   - Configure MLFlow tracking
   - Add custom knowledge base

2. **Deploy to Production**
   - Push image to registry
   - Apply Kubernetes manifests
   - Configure monitoring

3. **Customize Knowledge Base**
   - Add domain-specific troubleshooting docs
   - Fine-tune embedding model
   - Update prompt templates

4. **Set Up Monitoring**
   - Enable Prometheus metrics
   - Configure alerting
   - Set up log aggregation

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourorg/k8s-ai-incident-rca-assistant/issues
- Documentation: https://docs.example.com
- Slack Channel: #k8s-rca-support
