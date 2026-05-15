# Project Structure Overview

## Directory Structure

```
k8s-ai-incident-rca-assistant/
│
├── app/                              # Main application package
│   ├── __init__.py
│   │
│   ├── api/                         # REST API endpoints
│   │   ├── __init__.py
│   │   └── incident_api.py         # Incident management endpoints
│   │
│   ├── kubernetes/                  # Kubernetes integration
│   │   ├── __init__.py
│   │   ├── kube_client.py          # K8s API client
│   │   └── pod_logs.py             # Log analysis utility
│   │
│   ├── rag/                         # Retrieval-Augmented Generation
│   │   ├── __init__.py
│   │   ├── embedding.py            # Text embedding generation
│   │   ├── vector_store.py         # Vector storage and search
│   │   └── retriever.py            # RAG retriever
│   │
│   ├── llm/                         # Large Language Model integration
│   │   ├── __init__.py
│   │   ├── huggingface_client.py   # HuggingFace model client
│   │   └── prompt_template.py      # LLM prompt templates
│   │
│   ├── rca/                         # Root Cause Analysis engine
│   │   ├── __init__.py
│   │   └── rca_engine.py           # RCA analysis logic
│   │
│   ├── monitoring/                  # Monitoring and tracking
│   │   ├── __init__.py
│   │   └── mlflow_tracker.py       # MLFlow integration
│   │
│   └── notifications/               # Alert and notification system
│       ├── __init__.py
│       └── slack.py                # Slack notifier
│
├── tests/                           # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py                 # Pytest configuration and fixtures
│   ├── test_api.py                 # API endpoint tests
│   ├── test_rag.py                 # RAG component tests
│   └── test_pod_logs.py            # Log analysis tests
│
├── docs/                            # Documentation
│   ├── architecture.md             # Architecture documentation
│   └── screenshots/                # UI/API screenshots (optional)
│
├── kubernetes/                      # Kubernetes manifests
│   ├── deployment.yaml             # Deployment configuration
│   └── service.yaml                # Service and RBAC configs
│
├── .github/
│   └── workflows/
│       └── cicd.yml                # GitHub Actions CI/CD pipeline
│
├── main.py                         # Application entry point
├── dev.py                          # Development server
├── examples.py                     # Example usage code
│
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container image definition
├── docker-compose.yml              # Multi-service local setup
│
├── Makefile                        # Build and deployment commands
├── pytest.ini                      # Pytest configuration
│
├── README.md                       # Project overview and usage
├── INSTALLATION.md                 # Installation and setup guide
├── PROJECT_STRUCTURE.md            # This file
│
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore patterns
└── LICENSE                         # Project license

```

## Module Descriptions

### app/api (REST API)
- **Purpose**: Expose HTTP endpoints for incident management
- **Key Classes**:
  - `IncidentDetails`: Request model for incident creation
  - `RCAResult`: Response model for analysis results
  - Router functions for endpoints

### app/kubernetes (K8s Integration)
- **Purpose**: Interact with Kubernetes cluster
- **Key Classes**:
  - `KubernetesClient`: K8s API interaction
  - `PodLogAnalyzer`: Parse and analyze pod logs
- **Capabilities**:
  - Fetch pod logs and events
  - Get pod/node status and metrics
  - Analyze error patterns

### app/rag (Retrieval-Augmented Generation)
- **Purpose**: Knowledge retrieval and context augmentation
- **Key Classes**:
  - `EmbeddingGenerator`: Convert text to vectors
  - `VectorStore`: Store and search embeddings
  - `RAGRetriever`: Main RAG interface
- **Features**:
  - Sentence embedding generation
  - Similarity-based document retrieval
  - Knowledge base management

### app/llm (Large Language Models)
- **Purpose**: LLM-based analysis and generation
- **Key Classes**:
  - `HuggingFaceClient`: HuggingFace model interface
  - `PromptTemplate`: Prompt engineering
- **Features**:
  - Text generation
  - Error analysis
  - Fix suggestions

### app/rca (RCA Engine)
- **Purpose**: Main analysis logic combining all components
- **Key Classes**:
  - `RCAEngine`: Orchestrates RCA analysis
  - `RCAResult`: Structured analysis output
- **Process**:
  1. Gather pod/cluster data
  2. Analyze logs and patterns
  3. Retrieve relevant knowledge
  4. Use LLM to synthesize findings
  5. Return structured results

### app/monitoring (MLFlow)
- **Purpose**: Experiment and metric tracking
- **Key Classes**:
  - `MLFlowTracker`: MLFlow integration
- **Features**:
  - Log incident details
  - Track analysis metrics
  - Store analysis artifacts

### app/notifications (Slack)
- **Purpose**: Real-time incident alerts
- **Key Classes**:
  - `SlackNotifier`: Slack message sender
- **Features**:
  - Incident creation notifications
  - Analysis result notifications
  - Error alerts

## Data Flow

```
1. Incident Creation (API)
   ↓
2. Data Collection (Kubernetes)
   ├─ Pod logs
   ├─ Pod/node status
   └─ Events
   ↓
3. Analysis
   ├─ Log analysis (pattern detection)
   ├─ Knowledge retrieval (RAG)
   └─ LLM synthesis
   ↓
4. Result Structuring
   ├─ Root cause
   ├─ Contributing factors
   └─ Recommendations
   ↓
5. Storage & Notification
   ├─ MLFlow logging
   ├─ Database storage
   └─ Slack notification
```

## Key Dependencies

### Core Framework
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### ML/AI
- **HuggingFace Transformers**: LLM models
- **Sentence Transformers**: Embedding models
- **PyTorch**: Deep learning

### Kubernetes
- **kubernetes**: K8s Python client
- **PyYAML**: YAML parsing

### Infrastructure
- **MLFlow**: Experiment tracking
- **slack-sdk**: Slack integration

## Testing Strategy

### Test Organization
- **test_api.py**: Endpoint tests
- **test_rag.py**: RAG component tests
- **test_pod_logs.py**: Log analysis tests

### Test Fixtures (conftest.py)
- Sample pod data
- Sample error logs
- Event loop management

### Running Tests
```bash
pytest tests/ -v              # All tests
pytest tests/ --cov=app/      # With coverage
pytest -m "not slow"          # Fast tests only
```

## Development Workflow

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Set up .env file with configuration
3. Run dev server: `python dev.py`
4. Run tests: `pytest tests/ -v`

### Docker Development
1. Build image: `docker build -t k8s-incident-rca:latest .`
2. Run container: `docker run -p 8000:8000 -v ~/.kube/config:/app/.kube/config k8s-incident-rca:latest`
3. Access via: `http://localhost:8000`

### Kubernetes Deployment
1. Update image in manifests
2. Apply manifests: `kubectl apply -f kubernetes/`
3. Monitor deployment: `kubectl rollout status deployment/k8s-incident-rca`

## Configuration

### Environment Variables (.env)
- `LOG_LEVEL`: Python logging level
- `KUBECONFIG`: Path to kubeconfig
- `EMBEDDING_MODEL`: Sentence transformer model
- `MLFLOW_TRACKING_URI`: MLFlow server URI
- `SLACK_WEBHOOK_URL`: Slack webhook (optional)

### Kubernetes ConfigMap
- `mlflow_uri`: MLFlow server URL
- `log_level`: Application log level

### Kubernetes Secrets
- `slack_webhook_url`: Slack webhook URL

## Performance Characteristics

### Latency
- API response: <100ms
- K8s API call: 1-5s
- RAG retrieval: <500ms
- LLM inference: 5-30s
- Total RCA: 30-60s

### Resource Usage
- Memory: 512-1024 MB
- CPU: 500-1000 mCPU
- Disk: Minimal

### Scalability
- Horizontal scaling via HPA (2-5 replicas)
- Stateless design
- Load balanced via K8s Service

## Security Considerations

### API Security
- Input validation
- Rate limiting (recommended)
- CORS configuration

### Kubernetes Security
- RBAC for service account
- Network policies
- Non-root container
- Read-only filesystem

### Data Security
- Secrets in Kubernetes Secrets
- No sensitive data in logs
- Audit logging

## Future Enhancements

1. Multi-tenant support
2. Custom knowledge base ingestion
3. Automated remediation
4. Advanced analytics dashboard
5. Cost optimization insights
6. Integration with observability platforms
7. Fine-tuned domain-specific models
