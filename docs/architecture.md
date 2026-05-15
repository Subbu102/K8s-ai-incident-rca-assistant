# Architecture Documentation

## System Overview

The K8s AI Incident RCA Assistant is a distributed system designed to automatically detect, analyze, and provide root cause analysis for Kubernetes cluster incidents using advanced AI/ML techniques.

## Components

### 1. API Layer (FastAPI)
- **Incident Creation**: Accept incident reports
- **Status Queries**: Check analysis progress and results
- **Listing**: Query historical incidents
- **Async Processing**: Background RCA analysis

### 2. Kubernetes Integration
- **Pod Monitoring**: Access pod logs, events, and status
- **Node Analysis**: Collect node resource information
- **Cluster Awareness**: Understand cluster topology
- **RBAC Enforcement**: Secure cluster access

### 3. RAG System
- **Embedding Generator**: Convert text to vectors using sentence-transformers
- **Vector Store**: Efficient similarity search using in-memory store
- **Knowledge Retriever**: Find relevant troubleshooting documents
- **Knowledge Base**: Curated Kubernetes troubleshooting knowledge

### 4. LLM Integration
- **HuggingFace Models**: Use pre-trained LLMs for analysis
- **Prompt Engineering**: Custom prompts for RCA analysis
- **Context Injection**: Combine K8s data with LLM reasoning
- **Output Parsing**: Structure LLM output into findings

### 5. RCA Engine
- **Data Collection**: Gather logs, events, metrics
- **Pattern Detection**: Identify error signatures
- **Knowledge Matching**: Find similar past incidents
- **Analysis**: Synthesize findings into RCA report

### 6. Monitoring & Tracking
- **MLFlow Integration**: Experiment and incident logging
- **Metrics Tracking**: Performance and accuracy metrics
- **Artifact Storage**: Store analysis artifacts

### 7. Notifications
- **Slack Alerts**: Real-time incident notifications
- **Incident Summaries**: Formatted analysis reports
- **Action Items**: Recommended next steps

## Data Flow

```
1. Incident Reported
   ↓
2. API receives request
   ↓
3. Background task started
   ↓
4. Kubernetes data collected
   ├─ Pod logs fetched
   ├─ Pod status retrieved
   ├─ Events queried
   └─ Node info collected
   ↓
5. Logs analyzed
   ├─ Error patterns detected
   ├─ Stack traces extracted
   └─ Warnings identified
   ↓
6. Knowledge retrieved
   ├─ Error message embedded
   └─ Similar docs found via RAG
   ↓
7. LLM analysis
   ├─ Context compiled
   ├─ RCA prompt generated
   └─ Analysis generated
   ↓
8. Results structured
   ├─ Root cause identified
   ├─ Factors extracted
   └─ Recommendations generated
   ↓
9. Results stored
   ├─ MLFlow logging
   ├─ Database storage
   └─ Slack notification
   ↓
10. Client retrieves results
```

## Technology Stack

### Core
- **Python 3.11**: Primary language
- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server

### ML/AI
- **HuggingFace Transformers**: LLM access
- **Sentence Transformers**: Embedding generation
- **PyTorch**: Deep learning backend

### Kubernetes
- **kubernetes-client**: K8s API interaction
- **PyYAML**: Manifest parsing

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **MLFlow**: Experiment tracking

### Observability
- **Slack SDK**: Notifications
- **Python logging**: Application logging

## Security Considerations

### API Security
- Input validation on all endpoints
- Rate limiting (recommended)
- CORS configuration
- Request/response logging

### Kubernetes Security
- RBAC for service account
- Network policies for egress control
- Read-only root filesystem
- Non-root container execution
- Security context enforcement

### Data Security
- Secrets stored in Kubernetes Secrets
- Webhook URLs encrypted
- No sensitive data in logs
- Audit logging of RCA operations

## Performance Characteristics

### Latency
- API response: <100ms
- Log retrieval: 1-5 seconds
- RAG retrieval: <500ms
- LLM analysis: 5-30 seconds
- Total RCA time: ~30-60 seconds

### Throughput
- Single instance: ~10 concurrent incidents
- With 3 replicas: ~30 concurrent incidents
- Scaling via HPA up to 5 replicas

### Resource Usage
- Memory: 512-1024 MB per pod
- CPU: 500-1000 mCPU per pod
- Disk: Minimal (logs cleared)

## Scalability

### Horizontal Scaling
- HPA monitors CPU and memory
- Scale from 2 to 5 replicas
- Pod anti-affinity for distribution
- Session-less for state

### Vertical Scaling
- Increase resource limits
- Use faster LLM models
- Optimize embedding models
- Cache knowledge base

## Fault Tolerance

### Component Failures
- Service discovery via DNS
- Graceful degradation
- Retry logic for K8s API
- Fallback LLM responses

### Data Loss Prevention
- Vector store persistence
- MLFlow artifact storage
- Incident logging to disk

## Integration Points

### Kubernetes
- Direct API access via kubeconfig
- In-cluster config support
- Custom resource support

### External Services
- MLFlow tracking server
- Slack webhook/bot API
- Container registries (for images)

## Monitoring and Observability

### Metrics Exposed
- Request count and latency
- RCA analysis success rate
- Knowledge base hit rate
- Model inference time

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Component-specific loggers

### Health Checks
- Liveness probe: `/health`
- Readiness probe: `/health`
- Dependency checks at startup

## Future Enhancements

1. **Multi-tenant Support**: Isolate incidents by organization
2. **Advanced Analytics**: Trend analysis and prediction
3. **Automated Remediation**: Execute fixes automatically
4. **Cost Analysis**: Identify cost optimization opportunities
5. **Custom Models**: Fine-tuned models for specific domains
6. **Graph Analysis**: Dependency and blast radius analysis
7. **Integration Hub**: Connect with monitoring platforms
