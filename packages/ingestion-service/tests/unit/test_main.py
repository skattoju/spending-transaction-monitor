"""
Unit Tests for Ingestion Service
Tests individual components in isolation with mocking
"""

import datetime
import os

# Import from parent directory
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))



class TestTransactionTransformation:
    """Test transaction transformation logic"""
    
    def test_transform_transaction_success(self):
        """Test successful transaction transformation"""
        from src.common.models import IncomingTransaction
        from src.main import transform_transaction
        
        test_data = {
            'User': 1,
            'Card': 1,
            'Year': 2023,
            'Month': 1,
            'Day': 1,
            'Time': '12:00',
            'Amount': '$10.00',
            'Use Chip': 'Swipe Transaction',
            'Merchant Name': 123456789,
            'Merchant City': 'New York',
            'Merchant State': 'NY',
            'Zip': '10001',
            'MCC': 5411,
            'Errors?': '',
            'Is Fraud?': 'No'
        }
        
        incoming = IncomingTransaction(**test_data)
        result = transform_transaction(incoming)
        
        assert result.user == 1
        assert result.amount == 10.0
        assert result.is_fraud is False
        assert result.time == datetime.time(12, 0)

    def test_transform_transaction_fraud_yes(self):
        """Test transaction transformation with fraud=Yes"""
        from src.common.models import IncomingTransaction
        from src.main import transform_transaction
        
        test_data = {
            'User': 1,
            'Card': 1,
            'Year': 2023,
            'Month': 1,
            'Day': 1,
            'Time': '12:00',
            'Amount': '$10.00',
            'Use Chip': 'Swipe Transaction',
            'Merchant Name': 123456789,
            'Merchant City': 'New York',
            'Merchant State': 'NY',
            'Zip': '10001',
            'MCC': 5411,
            'Errors?': '',
            'Is Fraud?': 'Yes'
        }
        
        incoming = IncomingTransaction(**test_data)
        result = transform_transaction(incoming)
        
        assert result.is_fraud is True
