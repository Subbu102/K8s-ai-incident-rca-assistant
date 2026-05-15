"""
MLFlow integration for tracking experiments and incidents.
"""

import logging
from typing import Dict, Any, Optional

try:
    import mlflow
    from mlflow import log_metrics, log_params, log_artifact
except ImportError:
    mlflow = None

logger = logging.getLogger(__name__)


class MLFlowTracker:
    """MLFlow experiment and metric tracker."""
    
    def __init__(self, experiment_name: str = "k8s-rca", tracking_uri: Optional[str] = None):
        """
        Initialize MLFlow tracker.
        
        Args:
            experiment_name: Name of the MLFlow experiment
            tracking_uri: MLFlow tracking server URI
        """
        if mlflow is None:
            logger.warning("MLFlow not installed, tracking disabled")
            self.enabled = False
            return
        
        try:
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
            
            mlflow.set_experiment(experiment_name)
            self.enabled = True
            logger.info(f"MLFlow tracker initialized with experiment: {experiment_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MLFlow: {str(e)}")
            self.enabled = False
    
    def log_incident(self, incident_id: str, incident_data: Dict[str, Any], analysis_result: Dict[str, Any]):
        """
        Log incident analysis to MLFlow.
        
        Args:
            incident_id: Incident identifier
            incident_data: Incident details
            analysis_result: RCA analysis results
        """
        if not self.enabled:
            return
        
        try:
            with mlflow.start_run(run_name=f"incident-{incident_id}"):
                # Log parameters
                mlflow.log_params({
                    "pod_name": incident_data.get("pod_name", "unknown"),
                    "namespace": incident_data.get("namespace", "default"),
                    "severity": incident_data.get("severity", "medium")
                })
                
                # Log metrics
                mlflow.log_metrics({
                    "confidence_score": analysis_result.get("confidence_score", 0.0),
                    "num_factors": len(analysis_result.get("contributing_factors", [])),
                    "num_recommendations": len(analysis_result.get("recommendations", []))
                })
                
                # Log artifacts (as JSON)
                import json
                artifact_file = f"/tmp/incident_{incident_id}.json"
                with open(artifact_file, 'w') as f:
                    json.dump({
                        "incident": incident_data,
                        "analysis": analysis_result
                    }, f, indent=2, default=str)
                
                mlflow.log_artifact(artifact_file)
                
                logger.info(f"Logged incident {incident_id} to MLFlow")
                
        except Exception as e:
            logger.error(f"Failed to log incident to MLFlow: {str(e)}")
    
    def log_model_metrics(self, metrics: Dict[str, float], params: Dict[str, Any]):
        """
        Log model-related metrics.
        
        Args:
            metrics: Dictionary of metrics
            params: Dictionary of parameters
        """
        if not self.enabled:
            return
        
        try:
            with mlflow.start_run(run_name="model-metrics"):
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
                logger.info("Logged model metrics to MLFlow")
        except Exception as e:
            logger.error(f"Failed to log model metrics: {str(e)}")
    
    def close(self):
        """Close MLFlow session."""
        if self.enabled:
            try:
                mlflow.end_run()
                logger.info("MLFlow session closed")
            except Exception as e:
                logger.error(f"Error closing MLFlow: {str(e)}")
