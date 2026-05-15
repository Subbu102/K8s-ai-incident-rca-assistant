# K8s AI Incident RCA Assistant

## Overview

The **Kubernetes AI Incident RCA Assistant** is an intelligent system that automatically analyzes Kubernetes cluster incidents and provides root cause analysis (RCA) using:

- 🤖 **Large Language Models** (HuggingFace) for intelligent analysis
- 🔍 **Retrieval-Augmented Generation (RAG)** for contextual knowledge retrieval
- 📊 **Kubernetes Cluster Intelligence** for deep incident context
- 📈 **MLFlow Integration** for experiment tracking
- 💬 **Slack Integration** for incident notifications

## Features

### Core Capabilities
- **Automated Incident Detection**: Monitor Kubernetes cluster health
- **Intelligent RCA**: AI-powered root cause analysis
- **Knowledge Base**: Built-in troubleshooting knowledge base
- **Multi-source Analysis**: 
  - Pod logs and events
  - Node information and capacity
  - Container restart patterns
  - Error pattern detection
- **Recommendations**: Actionable remediation steps
- **Notifications**: Real-time Slack alerts

### Technical Features
- **RESTful API**: FastAPI-based async API
- **Scalable**: Horizontal Pod Autoscaler support
- **Secure**: RBAC, Network Policies, Non-root execution
- **Observable**: MLFlow tracking, Prometheus metrics
- **CI/CD**: GitHub Actions pipeline
- **Container-Ready**: Multi-stage Docker builds

## Architecture

```
┌─────────────┐
│   Client    │
│   (API)     │
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│   FastAPI Server            │
│  ┌────────────────────────┐ │
│  │  Incident API Router   │ │
│  └───────────┬────────────┘ │
│              │               │
│  ┌───────────▼────────────┐ │
│  │  RCA Engine            │ │
│  └───────────┬────────────┘ │
└──────┬───┬──────────┬────────┘
       │   │          │
   ┌───▼─┐ │      ┌───▼──────┐
   │RAG  │ │      │Kubernetes │
   │     │ │      │ Client    │
   └─────┘ │      └───────────┘
      ┌────▼──┐
      │ LLM   │
      └───────┘
```

## Installation

### Prerequisites
- Python 3.11+
- Kubernetes cluster (1.24+)
- Docker and Docker Buildx
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/yourorg/k8s-ai-incident-rca-assistant.git
cd k8s-ai-incident-rca-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export KUBECONFIG=~/.kube/config
export LOG_LEVEL=INFO

# Run application
python main.py
```

### Docker Build

```bash
# Build image
docker build -t k8s-incident-rca:latest .

# Run container
docker run -p 8000:8000 \
  -v ~/.kube/config:/app/.kube/config \
  k8s-incident-rca:latest
```

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f kubernetes/

# Verify deployment
kubectl get deployment k8s-incident-rca
kubectl logs deployment/k8s-incident-rca
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Incident
```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "pod_name": "app-pod-123",
    "namespace": "default",
    "error_message": "OOMKilled",
    "severity": "high"
  }'
```

### Get Incident Status
```bash
curl http://localhost:8000/api/v1/incidents/{incident_id}
```

### List Incidents
```bash
curl http://localhost:8000/api/v1/incidents?skip=0&limit=10
```

## Configuration

### Environment Variables
```bash
# Logging
LOG_LEVEL=INFO

# Kubernetes
KUBECONFIG=/path/to/kubeconfig
IN_CLUSTER=false

# LLM
HUGGINGFACE_MODEL=gpt2
HUGGINGFACE_TOKEN=your_token_here

# RAG
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_STORE_PATH=/tmp/vector_store

# Monitoring
MLFLOW_TRACKING_URI=http://mlflow:5000

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SLACK_TOKEN=your_slack_token
```

### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: k8s-incident-rca-config
data:
  mlflow_uri: "http://mlflow:5000"
  log_level: "INFO"
```

## Development

### Project Structure
```
app/
├── api/                    # REST API endpoints
│   └── incident_api.py
├── kubernetes/             # K8s integration
│   ├── kube_client.py     # K8s API client
│   └── pod_logs.py        # Log analysis
├── rag/                    # RAG components
│   ├── embedding.py       # Embedding generation
│   ├── vector_store.py    # Vector storage
│   └── retriever.py       # RAG retriever
├── llm/                    # LLM integration
│   ├── huggingface_client.py
│   └── prompt_template.py
├── rca/                    # RCA engine
│   └── rca_engine.py
├── monitoring/             # Observability
│   └── mlflow_tracker.py
└── notifications/          # Alerting
    └── slack.py
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --cov=app/

# Run with coverage report
pytest tests/ --cov=app/ --cov-report=html
```

### Code Quality
```bash
# Linting
flake8 app/
pylint app/

# Formatting
black app/
isort app/

# Type checking
mypy app/
```

## Performance Tuning

### RCA Engine Optimization
- Adjust embedding model for faster/more accurate retrieval
- Tune vector store batch size for memory efficiency
- Cache frequently accessed knowledge base entries

### API Optimization
- Enable response caching for repeated queries
- Use async/await for I/O operations
- Implement request rate limiting

### Kubernetes Optimization
- Adjust resource requests/limits based on workload
- Configure HPA with appropriate thresholds
- Use node affinity for optimal scheduling

## Troubleshooting

### Common Issues

**OOMKilled in Kubernetes**
```bash
# Increase memory limit
kubectl set resources deployment k8s-incident-rca -c=app --limits=memory=2Gi
```

**Cannot connect to K8s API**
```bash
# Verify ServiceAccount permissions
kubectl auth can-i get pods --as=system:serviceaccount:default:k8s-incident-rca
```

**Slow RCA Analysis**
```bash
# Check LLM model size
# Consider using smaller, faster model
# Reduce context window size
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:
- 📝 Open an issue on GitHub
- 💬 Join our Slack community
- 📧 Contact: support@example.com

## Roadmap

- [ ] Multi-language LLM support
- [ ] Custom knowledge base ingestion
- [ ] Advanced analytics dashboard
- [ ] Integration with observability platforms
- [ ] Incident trend analysis
- [ ] Automated remediation actions
- [ ] Cost analysis and optimization recommendations

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
- [Sentence Transformers](https://www.sbert.net/)
- [HuggingFace Transformers](https://huggingface.co/)
- [MLFlow](https://mlflow.org/)
