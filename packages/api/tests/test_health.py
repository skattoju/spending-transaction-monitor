"""
Health endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check_endpoint_exists():
    """Test health check endpoint is accessible"""
    response = client.get("/health/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least API service should be present


def test_health_check_includes_database():
    """Test health check includes database status"""
    response = client.get("/health/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Find database service in response
    db_service = next((s for s in data if s["name"] == "Database"), None)
    assert db_service is not None
    assert db_service["status"] in ["healthy", "down"]
    assert "message" in db_service
    assert db_service["version"] == "PostgreSQL"


def test_health_check_api_service():
    """Test health check includes API service"""
    response = client.get("/health/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # Find API service in response
    api_service = next((s for s in data if s["name"] == "API"), None)
    assert api_service is not None
    assert api_service["status"] == "healthy"
    assert api_service["message"] == "API is running"
    assert api_service["version"] == "0.0.0"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
