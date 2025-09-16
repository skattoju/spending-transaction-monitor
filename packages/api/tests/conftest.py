"""Shared test fixtures and configuration"""

import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from db.models import AlertRule, AlertType, Transaction


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Create a mock database session that can be reused across tests"""
    session = AsyncMock()
    # Add common mock behaviors
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def sample_user_id():
    """Standard user ID for testing"""
    return 'user-456'


@pytest.fixture
def sample_transaction_data():
    """Create sample transaction data as dict"""
    return {
        'id': 'tx-123',
        'user_id': 'user-456',
        'amount': Decimal('150.00'),
        'currency': 'USD',
        'merchant_name': 'Test Store',
        'merchant_category': 'Retail',
        'credit_card_num': '1234567890',
        'transaction_date': datetime(2024, 1, 15, 14, 30, 0),
        'trans_num': 'trans-789',
        'description': 'Test transaction',
        'status': 'completed',
    }


@pytest.fixture
def sample_transaction_obj(sample_transaction_data):
    """Create a mock Transaction object"""
    transaction = MagicMock(spec=Transaction)
    for key, value in sample_transaction_data.items():
        setattr(transaction, key, value)
    transaction.__dict__ = sample_transaction_data.copy()
    return transaction


@pytest.fixture
def sample_alert_rule_data():
    """Create sample alert rule data"""
    return {
        'id': 'rule-123',
        'user_id': 'user-456',
        'name': 'Large transaction alert',
        'description': 'Alert for large transactions',
        'natural_language_query': 'Alert me when transactions exceed $100',
        'is_active': True,
        'trigger_count': 5,
        'alert_type': AlertType.AMOUNT_THRESHOLD,
        'created_at': datetime(2024, 1, 1, 10, 0, 0),
        'updated_at': datetime(2024, 1, 1, 10, 0, 0),
    }


@pytest.fixture
def sample_alert_rule_obj(sample_alert_rule_data):
    """Create a mock AlertRule object"""
    rule = MagicMock(spec=AlertRule)
    for key, value in sample_alert_rule_data.items():
        setattr(rule, key, value)
    return rule


@pytest.fixture
def mock_llm_valid_response():
    """Mock LLM response for valid rule parsing"""
    return {
        'valid_sql': True,
        'alert_text': 'Alert me when transactions exceed $100',
        'sql_query': 'SELECT * FROM transactions WHERE amount > 100',
    }


@pytest.fixture
def mock_llm_invalid_response():
    """Mock LLM response for invalid rule parsing"""
    return {
        'valid_sql': False,
        'alert_text': 'Invalid rule text',
        'error': 'Could not parse rule',
    }


@pytest.fixture
def mock_llm_trigger_response():
    """Mock LLM response for alert triggering"""
    return {
        'should_trigger': True,
        'message': 'Large transaction detected: $150.00',
        'confidence': 0.95,
    }


@pytest.fixture
def mock_llm_no_trigger_response():
    """Mock LLM response for no alert triggering"""
    return {
        'should_trigger': False,
        'message': 'Transaction amount is within normal range',
        'confidence': 0.85,
    }
