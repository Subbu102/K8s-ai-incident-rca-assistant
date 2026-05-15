"""
Incident API endpoints for managing and analyzing Kubernetes incidents.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# Models
class IncidentDetails(BaseModel):
    """Incident details model."""
    pod_name: str = Field(..., description="Name of the affected pod")
    namespace: str = Field(..., description="Kubernetes namespace")
    error_message: str = Field(..., description="Error message or symptoms")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: Optional[str] = Field(default="medium", description="Severity level")
    additional_context: Optional[Dict[str, Any]] = Field(default=None)


class IncidentResponse(BaseModel):
    """Response model for incident creation."""
    incident_id: str = Field(..., description="Unique incident identifier")
    status: str = Field(..., description="Status of incident processing")
    message: str = Field(..., description="Response message")


class RCAResult(BaseModel):
    """RCA analysis result model."""
    incident_id: str = Field(..., description="Incident ID")
    root_cause: str = Field(..., description="Identified root cause")
    contributing_factors: List[str] = Field(default=[], description="Contributing factors")
    affected_resources: List[str] = Field(default=[], description="Affected Kubernetes resources")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of analysis")
    recommendations: List[str] = Field(default=[], description="Remediation recommendations")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class IncidentStatus(BaseModel):
    """Incident status response model."""
    incident_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    rca_result: Optional[RCAResult] = None


# Storage (in-memory for demo, replace with database)
incidents_store: Dict[str, Dict[str, Any]] = {}


@router.post("/incidents", response_model=IncidentResponse, tags=["incidents"])
async def create_incident(
    incident: IncidentDetails,
    background_tasks: BackgroundTasks
) -> IncidentResponse:
    """
    Create a new incident and trigger RCA analysis.
    
    Args:
        incident: Incident details
        background_tasks: Background tasks manager
        
    Returns:
        IncidentResponse with incident ID and status
    """
    try:
        incident_id = str(uuid4())
        
        # Store incident
        incidents_store[incident_id] = {
            "id": incident_id,
            "details": incident.dict(),
            "status": "processing",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "rca_result": None
        }
        
        # Add background task for RCA analysis
        background_tasks.add_task(analyze_incident, incident_id, incident)
        
        logger.info(f"Created incident {incident_id} for pod {incident.pod_name}")
        
        return IncidentResponse(
            incident_id=incident_id,
            status="processing",
            message=f"Incident created and analysis started. ID: {incident_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to create incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/{incident_id}", response_model=IncidentStatus, tags=["incidents"])
async def get_incident(incident_id: str) -> IncidentStatus:
    """
    Retrieve incident details and RCA results.
    
    Args:
        incident_id: The incident ID
        
    Returns:
        IncidentStatus with details and RCA results
    """
    if incident_id not in incidents_store:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident = incidents_store[incident_id]
    
    return IncidentStatus(
        incident_id=incident_id,
        status=incident["status"],
        created_at=incident["created_at"],
        updated_at=incident["updated_at"],
        rca_result=incident.get("rca_result")
    )


@router.get("/incidents", response_model=List[IncidentStatus], tags=["incidents"])
async def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
) -> List[IncidentStatus]:
    """
    List all incidents with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of incident statuses
    """
    incidents = list(incidents_store.values())[skip:skip + limit]
    
    return [
        IncidentStatus(
            incident_id=inc["id"],
            status=inc["status"],
            created_at=inc["created_at"],
            updated_at=inc["updated_at"],
            rca_result=inc.get("rca_result")
        )
        for inc in incidents
    ]


async def analyze_incident(incident_id: str, incident: IncidentDetails):
    """
    Background task to perform RCA analysis on incident.
    
    Args:
        incident_id: The incident ID
        incident: Incident details
    """
    from main import rca_engine, slack_notifier, mlflow_tracker
    
    try:
        logger.info(f"Starting RCA analysis for incident {incident_id}")
        
        if not rca_engine:
            logger.error("RCA engine not initialized")
            return
        
        # Perform RCA
        rca_result = await rca_engine.analyze(
            pod_name=incident.pod_name,
            namespace=incident.namespace,
            error_message=incident.error_message,
            context=incident.additional_context or {}
        )
        
        # Update incident with results
        incidents_store[incident_id]["rca_result"] = rca_result
        incidents_store[incident_id]["status"] = "completed"
        incidents_store[incident_id]["updated_at"] = datetime.utcnow()
        
        # Log to MLFlow
        if mlflow_tracker:
            mlflow_tracker.log_incident(incident_id, incident, rca_result)
        
        # Send Slack notification
        if slack_notifier:
            await slack_notifier.notify_incident_resolved(
                incident_id=incident_id,
                pod_name=incident.pod_name,
                root_cause=rca_result.root_cause,
                recommendations=rca_result.recommendations
            )
        
        logger.info(f"RCA analysis completed for incident {incident_id}")
        
    except Exception as e:
        logger.error(f"Error analyzing incident {incident_id}: {str(e)}")
        incidents_store[incident_id]["status"] = "failed"
        incidents_store[incident_id]["updated_at"] = datetime.utcnow()
