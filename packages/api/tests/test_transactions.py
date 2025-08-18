"""Tests for transaction endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.main import app
from src.schemas.transaction import TransactionType, TransactionStatus

client = TestClient(app)


class TestUserSetup:
    """Setup user and credit card for transaction tests"""
    
    def setup_method(self):
        """Create a test user and credit card before each test"""
        self.user_payload = {
            "email": "transaction.test@example.com",
            "firstName": "Transaction",
            "lastName": "Tester",
            "phoneNumber": "+1-555-8888"
        }
        
        # Create user
        response = client.post("/users", json=self.user_payload)
        if response.status_code == 200:
            self.user_id = response.json()["id"]
        else:
            # User might already exist, try to get it
            response = client.get("/users")
            users = response.json()
            if users:
                self.user_id = users[0]["id"]
            else:
                pytest.fail("Could not create or find a test user")
        
        # Create credit card for the user
        self.card_payload = {
            "userId": self.user_id,
            "cardNumber": "1234",
            "cardType": "Visa",
            "bankName": "Test Bank",
            "cardHolderName": "Transaction Tester",
            "expiryMonth": 12,
            "expiryYear": 2027,
            "isActive": True
        }
        
        response = client.post("/transactions/cards", json=self.card_payload)
        if response.status_code == 200:
            self.card_id = response.json()["id"]
        else:
            pytest.fail("Could not create a test credit card")


class TestTransactions(TestUserSetup):
    """Test transaction endpoints"""

    def test_get_transactions_empty(self):
        """Test getting transactions when none exist"""
        response = client.get("/transactions")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_transaction(self):
        """Test creating a new transaction"""
        payload = {
            "id": str(uuid.uuid4()),
            "userId": self.user_id,
            "creditCardId": self.card_id,
            "amount": 99.99,
            "currency": "USD",
            "description": "Test purchase",
            "merchantName": "Test Store",
            "merchantCategory": "Retail",
            "transactionDate": "2024-01-15T10:30:00Z",
            "transactionType": "PURCHASE",
            "merchantCity": "San Francisco",
            "merchantState": "CA",
            "merchantCountry": "US",
            "status": "APPROVED"
        }
        
        response = client.post("/transactions", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["amount"] == payload["amount"]
        assert data["description"] == payload["description"]
        assert data["merchantName"] == payload["merchantName"]
        assert data["transactionType"] == payload["transactionType"]
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_transaction_invalid_user(self):
        """Test creating transaction with non-existent user"""
        payload = {
            "id": str(uuid.uuid4()),
            "userId": "non-existent-user",
            "creditCardId": self.card_id,
            "amount": 99.99,
            "currency": "USD",
            "description": "Test purchase",
            "merchantName": "Test Store",
            "merchantCategory": "Retail",
            "transactionDate": "2024-01-15T10:30:00Z",
            "transactionType": "PURCHASE",
            "status": "APPROVED"
        }
        
        response = client.post("/transactions", json=payload)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_create_transaction_invalid_card(self):
        """Test creating transaction with non-existent credit card"""
        payload = {
            "id": str(uuid.uuid4()),
            "userId": self.user_id,
            "creditCardId": "non-existent-card",
            "amount": 99.99,
            "currency": "USD",
            "description": "Test purchase",
            "merchantName": "Test Store",
            "merchantCategory": "Retail",
            "transactionDate": "2024-01-15T10:30:00Z",
            "transactionType": "PURCHASE",
            "status": "APPROVED"
        }
        
        response = client.post("/transactions", json=payload)
        assert response.status_code == 404
        assert "Credit card not found" in response.json()["detail"]

    def test_get_transaction_by_id(self):
        """Test getting a specific transaction"""
        # First create a transaction
        create_payload = {
            "id": str(uuid.uuid4()),
            "userId": self.user_id,
            "creditCardId": self.card_id,
            "amount": 150.00,
            "currency": "USD",
            "description": "Test transaction",
            "merchantName": "Test Merchant",
            "merchantCategory": "Food",
            "transactionDate": "2024-01-16T12:00:00Z",
            "transactionType": "PURCHASE",
            "status": "APPROVED"
        }
        
        create_response = client.post("/transactions", json=create_payload)
        transaction_id = create_response.json()["id"]
        
        # Then get it by ID
        response = client.get(f"/transactions/{transaction_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == transaction_id
        assert data["amount"] == create_payload["amount"]
        assert data["description"] == create_payload["description"]

    def test_get_transaction_not_found(self):
        """Test getting non-existent transaction"""
        response = client.get("/transactions/non-existent-id")
        assert response.status_code == 404
        assert "Transaction not found" in response.json()["detail"]

    def test_update_transaction(self):
        """Test updating a transaction"""
        # First create a transaction
        create_payload = {
            "id": str(uuid.uuid4()),
            "userId": self.user_id,
            "creditCardId": self.card_id,
            "amount": 200.00,
            "currency": "USD",
            "description": "Original description",
            "merchantName": "Original Merchant",
            "merchantCategory": "Electronics",
            "transactionDate": "2024-01-17T14:00:00Z",
            "transactionType": "PURCHASE",
            "status": "PENDING"
        }
        
        create_response = client.post("/transactions", json=create_payload)
        transaction_id = create_response.json()["id"]
        
        # Then update it
        update_payload = {
            "description": "Updated description",
            "status": "APPROVED",
            "amount": 225.00
        }
        
        response = client.put(f"/transactions/{transaction_id}", json=update_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["description"] == update_payload["description"]
        assert data["status"] == update_payload["status"]
        assert data["amount"] == update_payload["amount"]

    def test_delete_transaction(self):
        """Test deleting a transaction"""
        # First create a transaction
        create_payload = {
            "id": str(uuid.uuid4()),
            "userId": self.user_id,
            "creditCardId": self.card_id,
            "amount": 75.00,
            "currency": "USD",
            "description": "To delete",
            "merchantName": "Delete Store",
            "merchantCategory": "Retail",
            "transactionDate": "2024-01-18T16:00:00Z",
            "transactionType": "PURCHASE",
            "status": "APPROVED"
        }
        
        create_response = client.post("/transactions", json=create_payload)
        transaction_id = create_response.json()["id"]
        
        # Then delete it
        response = client.delete(f"/transactions/{transaction_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Transaction deleted successfully"
        
        # Verify it's gone
        get_response = client.get(f"/transactions/{transaction_id}")
        assert get_response.status_code == 404

    def test_filter_transactions(self):
        """Test filtering transactions"""
        # Create multiple transactions
        transactions = [
            {
                "id": str(uuid.uuid4()),
                "userId": self.user_id,
                "creditCardId": self.card_id,
                "amount": 50.00,
                "currency": "USD",
                "description": "Small purchase",
                "merchantName": "Small Store",
                "merchantCategory": "Retail",
                "transactionDate": "2024-01-19T10:00:00Z",
                "transactionType": "PURCHASE",
                "status": "APPROVED"
            },
            {
                "id": str(uuid.uuid4()),
                "userId": self.user_id,
                "creditCardId": self.card_id,
                "amount": 500.00,
                "currency": "USD",
                "description": "Large purchase",
                "merchantName": "Large Store",
                "merchantCategory": "Electronics",
                "transactionDate": "2024-01-20T11:00:00Z",
                "transactionType": "PURCHASE",
                "status": "APPROVED"
            }
        ]
        
        for tx in transactions:
            client.post("/transactions", json=tx)
        
        # Test filtering by user
        response = client.get(f"/transactions?user_id={self.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert all(tx["userId"] == self.user_id for tx in data)
        
        # Test filtering by amount
        response = client.get(f"/transactions?user_id={self.user_id}&min_amount=100")
        assert response.status_code == 200
        data = response.json()
        assert all(tx["amount"] >= 100 for tx in data)
        
        # Test filtering by category
        response = client.get(f"/transactions?user_id={self.user_id}&merchant_category=Electronics")
        assert response.status_code == 200
        data = response.json()
        assert all(tx["merchantCategory"] == "Electronics" for tx in data)


class TestCreditCards(TestUserSetup):
    """Test credit card endpoints"""

    def test_get_credit_cards(self):
        """Test getting credit cards"""
        response = client.get(f"/transactions/cards?user_id={self.user_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(card["userId"] == self.user_id for card in data)

    def test_get_credit_card_by_id(self):
        """Test getting a specific credit card"""
        response = client.get(f"/transactions/cards/{self.card_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == self.card_id
        assert data["userId"] == self.user_id
        assert data["cardNumber"] == self.card_payload["cardNumber"]

    def test_get_credit_card_not_found(self):
        """Test getting non-existent credit card"""
        response = client.get("/transactions/cards/non-existent-id")
        assert response.status_code == 404
        assert "Credit card not found" in response.json()["detail"]

    def test_create_credit_card(self):
        """Test creating a new credit card"""
        payload = {
            "userId": self.user_id,
            "cardNumber": "5678",
            "cardType": "Mastercard",
            "bankName": "Another Bank",
            "cardHolderName": "Test User",
            "expiryMonth": 6,
            "expiryYear": 2028,
            "isActive": True
        }
        
        response = client.post("/transactions/cards", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["cardNumber"] == payload["cardNumber"]
        assert data["cardType"] == payload["cardType"]
        assert data["userId"] == self.user_id
        assert "id" in data
        assert "createdAt" in data

    def test_create_credit_card_invalid_user(self):
        """Test creating credit card with non-existent user"""
        payload = {
            "userId": "non-existent-user",
            "cardNumber": "9999",
            "cardType": "Visa",
            "bankName": "Test Bank",
            "cardHolderName": "Test User",
            "expiryMonth": 12,
            "expiryYear": 2027,
            "isActive": True
        }
        
        response = client.post("/transactions/cards", json=payload)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_update_credit_card(self):
        """Test updating a credit card"""
        update_payload = {
            "cardHolderName": "Updated Name",
            "isActive": False
        }
        
        response = client.put(f"/transactions/cards/{self.card_id}", json=update_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["cardHolderName"] == update_payload["cardHolderName"]
        assert data["isActive"] == update_payload["isActive"]

    def test_delete_credit_card(self):
        """Test deleting a credit card"""
        # Create a card to delete
        payload = {
            "userId": self.user_id,
            "cardNumber": "9999",
            "cardType": "Visa",
            "bankName": "Test Bank",
            "cardHolderName": "To Delete",
            "expiryMonth": 12,
            "expiryYear": 2027,
            "isActive": True
        }
        
        create_response = client.post("/transactions/cards", json=payload)
        card_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/transactions/cards/{card_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Credit card deleted successfully"
        
        # Verify it's gone
        get_response = client.get(f"/transactions/cards/{card_id}")
        assert get_response.status_code == 404


class TestTransactionAnalysis(TestUserSetup):
    """Test transaction analysis endpoints"""

    def test_get_transaction_summary(self):
        """Test getting transaction summary"""
        # Create some transactions first
        transactions = [
            {
                "id": str(uuid.uuid4()),
                "userId": self.user_id,
                "creditCardId": self.card_id,
                "amount": 100.00,
                "currency": "USD",
                "description": "Transaction 1",
                "merchantName": "Store 1",
                "merchantCategory": "Retail",
                "transactionDate": "2024-01-21T10:00:00Z",
                "transactionType": "PURCHASE",
                "status": "APPROVED"
            },
            {
                "id": str(uuid.uuid4()),
                "userId": self.user_id,
                "creditCardId": self.card_id,
                "amount": 200.00,
                "currency": "USD",
                "description": "Transaction 2",
                "merchantName": "Store 2",
                "merchantCategory": "Electronics",
                "transactionDate": "2024-01-22T11:00:00Z",
                "transactionType": "PURCHASE",
                "status": "APPROVED"
            }
        ]
        
        for tx in transactions:
            client.post("/transactions", json=tx)
        
        # Get summary
        response = client.get(f"/transactions/analysis/summary/{self.user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["totalTransactions"] >= 2
        assert data["totalAmount"] >= 300.0
        assert data["averageAmount"] >= 150.0
        assert data["largestTransaction"] >= 200.0
        assert data["smallestTransaction"] >= 100.0

    def test_get_category_spending(self):
        """Test getting category spending breakdown"""
        # Create transactions in different categories
        transactions = [
            {
                "id": str(uuid.uuid4()),
                "userId": self.user_id,
                "creditCardId": self.card_id,
                "amount": 50.00,
                "currency": "USD",
                "description": "Food purchase",
                "merchantName": "Restaurant",
                "merchantCategory": "Food",
                "transactionDate": "2024-01-23T12:00:00Z",
                "transactionType": "PURCHASE",
                "status": "APPROVED"
            },
            {
                "id": str(uuid.uuid4()),
                "userId": self.user_id,
                "creditCardId": self.card_id,
                "amount": 75.00,
                "currency": "USD",
                "description": "More food",
                "merchantName": "Cafe",
                "merchantCategory": "Food",
                "transactionDate": "2024-01-24T13:00:00Z",
                "transactionType": "PURCHASE",
                "status": "APPROVED"
            }
        ]
        
        for tx in transactions:
            client.post("/transactions", json=tx)
        
        # Get category breakdown
        response = client.get(f"/transactions/analysis/categories/{self.user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        
        # Find Food category
        food_category = next((cat for cat in data if cat["category"] == "Food"), None)
        if food_category:
            assert food_category["totalAmount"] >= 125.0
            assert food_category["transactionCount"] >= 2
            assert food_category["averageAmount"] >= 62.5

    def test_get_transaction_summary_invalid_user(self):
        """Test getting summary for non-existent user"""
        response = client.get("/transactions/analysis/summary/non-existent-user")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_category_spending_invalid_user(self):
        """Test getting category breakdown for non-existent user"""
        response = client.get("/transactions/analysis/categories/non-existent-user")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestUserTransactions(TestUserSetup):
    """Test user-specific transaction endpoints"""

    def test_get_user_transactions(self):
        """Test getting transactions for a specific user"""
        # Create a transaction for the user
        tx_payload = {
            "id": str(uuid.uuid4()),
            "userId": self.user_id,
            "creditCardId": self.card_id,
            "amount": 150.00,
            "currency": "USD",
            "description": "User transaction",
            "merchantName": "User Store",
            "merchantCategory": "Retail",
            "transactionDate": "2024-01-25T14:00:00Z",
            "transactionType": "PURCHASE",
            "status": "APPROVED"
        }
        
        client.post("/transactions", json=tx_payload)
        
        # Get user transactions
        response = client.get(f"/users/{self.user_id}/transactions")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert all(tx["userId"] == self.user_id for tx in data)

    def test_get_user_credit_cards(self):
        """Test getting credit cards for a specific user"""
        response = client.get(f"/users/{self.user_id}/credit-cards")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert all(card["userId"] == self.user_id for card in data)

    def test_get_user_credit_cards_active_only(self):
        """Test getting only active credit cards for a user"""
        response = client.get(f"/users/{self.user_id}/credit-cards?is_active=true")
        assert response.status_code == 200
        
        data = response.json()
        assert all(card["isActive"] for card in data)

    def test_get_user_transactions_invalid_user(self):
        """Test getting transactions for non-existent user"""
        response = client.get("/users/non-existent-user/transactions")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_user_credit_cards_invalid_user(self):
        """Test getting credit cards for non-existent user"""
        response = client.get("/users/non-existent-user/credit-cards")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
