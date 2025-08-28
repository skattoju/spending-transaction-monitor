"""
Simple tests that don't require external dependencies
"""


def test_import_main():
    """Test that the main module can be imported"""
    from src.main import app

    assert app is not None
    assert app.title == 'spending-monitor API'


def test_import_routes():
    """Test that routes can be imported"""
    from src.routes import alerts, health, transactions, users

    assert health.router is not None
    assert transactions.router is not None
    assert users.router is not None
    assert alerts.router is not None


def test_import_models():
    """Test that models can be imported"""
    from db.models import AlertNotification, AlertRule, Transaction, User

    assert User is not None
    assert Transaction is not None
    assert AlertRule is not None
    assert AlertNotification is not None
