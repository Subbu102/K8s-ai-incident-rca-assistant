"""
Unit tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.api.incident_api import IncidentDetails


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "name" in response.json()
        assert "version" in response.json()


class TestIncidentEndpoints:
    """Test incident API endpoints."""
    
    def test_create_incident(self):
        """Test creating an incident."""
        incident_data = {
            "pod_name": "test-pod",
            "namespace": "default",
            "error_message": "Test error",
            "severity": "medium"
        }
        
        response = client.post("/api/v1/incidents", json=incident_data)
        
        assert response.status_code == 200
        assert "incident_id" in response.json()
        assert response.json()["status"] == "processing"
    
    def test_list_incidents(self):
        """Test listing incidents."""
        response = client.get("/api/v1/incidents")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_incidents_pagination(self):
        """Test incident listing with pagination."""
        response = client.get("/api/v1/incidents?skip=0&limit=5")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
