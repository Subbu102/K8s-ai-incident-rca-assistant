"""
Main entry point for the Kubernetes AI Incident RCA Assistant.
Initializes and runs the FastAPI application with integrated RAG and LLM components.
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.api.incident_api import router as incident_router
from app.kubernetes.kube_client import KubernetesClient
from app.rag.retriever import RAGRetriever
from app.llm.huggingface_client import HuggingFaceClient
from app.rca.rca_engine import RCAEngine
from app.monitoring.mlflow_tracker import MLFlowTracker
from app.notifications.slack import SlackNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global components
kube_client: Optional[KubernetesClient] = None
rag_retriever: Optional[RAGRetriever] = None
llm_client: Optional[HuggingFaceClient] = None
rca_engine: Optional[RCAEngine] = None
mlflow_tracker: Optional[MLFlowTracker] = None
slack_notifier: Optional[SlackNotifier] = None


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Initializing K8s AI Incident RCA Assistant...")
    
    try:
        global kube_client, rag_retriever, llm_client, rca_engine, mlflow_tracker, slack_notifier
        
        # Initialize Kubernetes client
        logger.info("📦 Initializing Kubernetes client...")
        kube_client = KubernetesClient()
        
        # Initialize RAG components
        logger.info("🔍 Initializing RAG retriever...")
        rag_retriever = RAGRetriever()
        
        # Initialize LLM client
        logger.info("🤖 Initializing HuggingFace LLM client...")
        llm_client = HuggingFaceClient()
        
        # Initialize RCA engine
        logger.info("🔎 Initializing RCA engine...")
        rca_engine = RCAEngine(rag_retriever=rag_retriever, llm_client=llm_client)
        
        # Initialize monitoring
        logger.info("📊 Initializing MLFlow tracker...")
        mlflow_tracker = MLFlowTracker()
        
        # Initialize notifications
        logger.info("💬 Initializing Slack notifier...")
        slack_notifier = SlackNotifier()
        
        logger.info("✅ Initialization complete!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down K8s AI Incident RCA Assistant...")
    try:
        if mlflow_tracker:
            mlflow_tracker.close()
        logger.info("👋 Shutdown complete!")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="K8s AI Incident RCA Assistant",
    description="AI-powered root cause analysis for Kubernetes incidents using RAG and LLMs",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incident_router, prefix="/api/v1", tags=["incidents"])


@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return HealthCheck(status="healthy", version="1.0.0")


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "name": "K8s AI Incident RCA Assistant",
        "version": "1.0.0",
        "description": "AI-powered root cause analysis for Kubernetes incidents",
        "endpoints": {
            "health": "/health",
            "api": "/api/v1",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
