"""
Integration Tests for Ingestion Service
Tests the full FastAPI application with TestClient
"""

import os

# Import from parent directory
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from main import app


class TestIngestionServiceIntegration:
    """Integration tests using FastAPI TestClient"""

    def test_create_transaction_success(self):
        """Test successful transaction creation through API"""
        
        with TestClient(app) as client:
            incoming_transaction = {
                "User": 1,
                "Card": 1,
                "Year": 2023,
                "Month": 1,
                "Day": 1,
                "Time": "12:00",
                "Amount": "$10.00",
                "Use Chip": "Swipe Transaction",
                "Merchant Name": 123456789,
                "Merchant City": "New York",
                "Merchant State": "NY",
                "Zip": "10001",
                "MCC": 5411,
                "Errors?": "",
                "Is Fraud?": "No"
            }
            response = client.post("/transactions/", json=incoming_transaction)
            
            assert response.status_code == 200
            
            expected_response = {
                "user": 1,
                "card": 1,
                "year": 2023,
                "month": 1,
                "day": 1,
                "time": "12:00:00",
                "amount": 10.0,
                "use_chip": "Swipe Transaction",
                "merchant_id": 123456789,
                "merchant_city": "New York",
                "merchant_state": "NY",
                "zip": "10001",
                "mcc": 5411,
                "errors": "",
                "is_fraud": False
            }
            assert response.json() == expected_response
            

    def test_create_transaction_simple(self):
        """Test simple transaction creation"""
        
        with TestClient(app) as client:
            incoming_transaction = {
                "User": 1,
                "Card": 1,
                "Year": 2023,
                "Month": 1,
                "Day": 1,
                "Time": "12:00",
                "Amount": "$10.00",
                "Use Chip": "Swipe Transaction",
                "Merchant Name": 123456789,
                "Merchant City": "New York",
                "Merchant State": "NY",
                "Zip": "10001",
                "MCC": 5411,
                "Errors?": "",
                "Is Fraud?": "No"
            }
            response = client.post("/transactions/", json=incoming_transaction)
            
            # Should return 200
            assert response.status_code == 200
            response_data = response.json()
            assert "user" in response_data
            assert response_data["user"] == 1

    def test_healthz(self):
        """Test the simple health check endpoint"""
        with TestClient(app) as client:
            response = client.get("/healthz")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    def test_health_check(self):
        """Test health check endpoint"""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "ingestion-service"

    def test_invalid_transaction_data(self):
        """Test API with invalid transaction data"""
        with TestClient(app) as client:
            invalid_transaction = {
                "User": "not-a-number",  # Invalid type
                "Card": 1
                # Missing required fields
            }
            response = client.post("/transactions/", json=invalid_transaction)
            
            # Should return validation error
            assert response.status_code == 422

    def test_missing_endpoint(self):
        """Test accessing non-existent endpoint"""
        with TestClient(app) as client:
            response = client.get("/non-existent")
            assert response.status_code == 404
