"""Tests for alert endpoints"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestUserSetup:
    """Setup user for alert tests"""

    def setup_method(self):
        """Create a test user before each test"""
        self.user_payload = {
            'email': 'alert.test@example.com',
            'firstName': 'Alert',
            'lastName': 'Tester',
            'phoneNumber': '+1-555-9999',
        }

        # Create user
        response = client.post('/users', json=self.user_payload)
        if response.status_code == 200:
            self.user_id = response.json()['id']
        else:
            # User might already exist, try to get it
            response = client.get('/users')
            users = response.json()
            if users:
                self.user_id = users[0]['id']
            else:
                pytest.fail('Could not create or find a test user')


class TestAlertRules(TestUserSetup):
    """Test alert rule endpoints"""

    def test_get_alert_rules_empty(self):
        """Test getting alert rules when none exist"""
        response = client.get('/alerts/rules')
        assert response.status_code == 200
        assert response.json() == []

    def test_create_alert_rule(self):
        """Test creating a new alert rule"""
        payload = {
            'userId': self.user_id,
            'name': 'High Amount Alert',
            'description': 'Alert for transactions over $1000',
            'isActive': True,
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 1000.0,
            'notificationMethods': ['EMAIL', 'PUSH'],
        }

        response = client.post('/alerts/rules', json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['name'] == payload['name']
        assert data['alertType'] == payload['alertType']
        assert data['amountThreshold'] == payload['amountThreshold']
        assert data['isActive'] == payload['isActive']
        assert 'id' in data
        assert 'createdAt' in data
        assert 'updatedAt' in data

    def test_create_alert_rule_invalid_user(self):
        """Test creating alert rule with non-existent user"""
        payload = {
            'userId': 'non-existent-user',
            'name': 'Test Alert',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
        }

        response = client.post('/alerts/rules', json=payload)
        assert response.status_code == 404
        assert 'User not found' in response.json()['detail']

    def test_get_alert_rule_by_id(self):
        """Test getting a specific alert rule"""
        # First create a rule
        create_payload = {
            'userId': self.user_id,
            'name': 'Test Rule',
            'alertType': 'MERCHANT_CATEGORY',
            'merchantCategory': 'RESTAURANTS',
        }

        create_response = client.post('/alerts/rules', json=create_payload)
        rule_id = create_response.json()['id']

        # Then get it by ID
        response = client.get(f'/alerts/rules/{rule_id}')
        assert response.status_code == 200

        data = response.json()
        assert data['id'] == rule_id
        assert data['name'] == create_payload['name']
        assert data['alertType'] == create_payload['alertType']

    def test_get_alert_rule_not_found(self):
        """Test getting non-existent alert rule"""
        response = client.get('/alerts/rules/non-existent-id')
        assert response.status_code == 404
        assert 'Alert rule not found' in response.json()['detail']

    def test_update_alert_rule(self):
        """Test updating an alert rule"""
        # First create a rule
        create_payload = {
            'userId': self.user_id,
            'name': 'Original Name',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 500.0,
        }

        create_response = client.post('/alerts/rules', json=create_payload)
        rule_id = create_response.json()['id']

        # Then update it
        update_payload = {
            'name': 'Updated Name',
            'amountThreshold': 750.0,
            'isActive': False,
        }

        response = client.put(f'/alerts/rules/{rule_id}', json=update_payload)
        assert response.status_code == 200

        data = response.json()
        assert data['name'] == update_payload['name']
        assert data['amountThreshold'] == update_payload['amountThreshold']
        assert data['isActive'] == update_payload['isActive']

    def test_delete_alert_rule(self):
        """Test deleting an alert rule"""
        # First create a rule
        create_payload = {
            'userId': self.user_id,
            'name': 'To Delete',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
        }

        create_response = client.post('/alerts/rules', json=create_payload)
        rule_id = create_response.json()['id']

        # Then delete it
        response = client.delete(f'/alerts/rules/{rule_id}')
        assert response.status_code == 200
        assert response.json()['message'] == 'Alert rule deleted successfully'

        # Verify it's gone
        get_response = client.get(f'/alerts/rules/{rule_id}')
        assert get_response.status_code == 404

    def test_filter_alert_rules(self):
        """Test filtering alert rules"""
        # Create multiple rules
        rules = [
            {
                'userId': 'user-1',
                'name': 'Rule 1',
                'alertType': 'AMOUNT_THRESHOLD',
                'amountThreshold': 100.0,
                'isActive': True,
            },
            {
                'userId': 'user-2',
                'name': 'Rule 2',
                'alertType': 'MERCHANT_CATEGORY',
                'merchantCategory': 'SHOPPING',
                'isActive': False,
            },
        ]

        for rule in rules:
            client.post('/alerts/rules', json=rule)

        # Test filtering by user
        response = client.get('/alerts/rules?user_id=user-1')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['userId'] == 'user-1'

        # Test filtering by active status
        response = client.get('/alerts/rules?is_active=true')
        assert response.status_code == 200
        data = response.json()
        assert all(rule['isActive'] for rule in data)


class TestAlertNotifications(TestUserSetup):
    """Test alert notification endpoints"""

    def test_get_alert_notifications_empty(self):
        """Test getting notifications when none exist"""
        response = client.get('/alerts/notifications')
        assert response.status_code == 200
        assert response.json() == []

    def test_create_alert_notification(self):
        """Test creating a new alert notification"""
        # First create an alert rule
        rule_payload = {
            'userId': self.user_id,
            'name': 'Test Rule',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Then create a notification
        notification_payload = {
            'userId': self.user_id,
            'alertRuleId': rule_id,
            'title': 'High Transaction Alert',
            'message': 'Transaction over $100 detected',
            'notificationMethod': 'EMAIL',
            'status': 'PENDING',
        }

        response = client.post('/alerts/notifications', json=notification_payload)
        assert response.status_code == 200

        data = response.json()
        assert data['title'] == notification_payload['title']
        assert data['message'] == notification_payload['message']
        assert data['notificationMethod'] == notification_payload['notificationMethod']
        assert data['status'] == notification_payload['status']
        assert 'id' in data
        assert 'createdAt' in data

    def test_create_notification_invalid_user(self):
        """Test creating notification with non-existent user"""
        payload = {
            'userId': 'non-existent-user',
            'alertRuleId': 'some-rule-id',
            'title': 'Test',
            'message': 'Test message',
            'notificationMethod': 'EMAIL',
            'status': 'PENDING',
        }

        response = client.post('/alerts/notifications', json=payload)
        assert response.status_code == 404
        assert 'User not found' in response.json()['detail']

    def test_create_notification_invalid_rule(self):
        """Test creating notification with non-existent alert rule"""
        payload = {
            'userId': 'test-user-123',
            'alertRuleId': 'non-existent-rule',
            'title': 'Test',
            'message': 'Test message',
            'notificationMethod': 'EMAIL',
            'status': 'PENDING',
        }

        response = client.post('/alerts/notifications', json=payload)
        assert response.status_code == 404
        assert 'Alert rule not found' in response.json()['detail']

    def test_get_notification_by_id(self):
        """Test getting a specific notification"""
        # Create rule and notification
        rule_payload = {
            'userId': 'test-user-123',
            'name': 'Test Rule',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        notification_payload = {
            'userId': 'test-user-123',
            'alertRuleId': rule_id,
            'title': 'Test Notification',
            'message': 'Test message',
            'notificationMethod': 'SMS',
            'status': 'SENT',
        }

        create_response = client.post(
            '/alerts/notifications', json=notification_payload
        )
        notification_id = create_response.json()['id']

        # Get by ID
        response = client.get(f'/alerts/notifications/{notification_id}')
        assert response.status_code == 200

        data = response.json()
        assert data['id'] == notification_id
        assert data['title'] == notification_payload['title']
        assert data['notificationMethod'] == notification_payload['notificationMethod']

    def test_update_notification(self):
        """Test updating a notification"""
        # Create rule and notification
        rule_payload = {
            'userId': 'test-user-123',
            'name': 'Test Rule',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        notification_payload = {
            'userId': 'test-user-123',
            'alertRuleId': rule_id,
            'title': 'Original Title',
            'message': 'Original message',
            'notificationMethod': 'EMAIL',
            'status': 'PENDING',
        }

        create_response = client.post(
            '/alerts/notifications', json=notification_payload
        )
        notification_id = create_response.json()['id']

        # Update it
        update_payload = {'title': 'Updated Title', 'status': 'DELIVERED'}

        response = client.put(
            f'/alerts/notifications/{notification_id}', json=update_payload
        )
        assert response.status_code == 200

        data = response.json()
        assert data['title'] == update_payload['title']
        assert data['status'] == update_payload['status']

    def test_delete_notification(self):
        """Test deleting a notification"""
        # Create rule and notification
        rule_payload = {
            'userId': 'test-user-123',
            'name': 'Test Rule',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        notification_payload = {
            'userId': 'test-user-123',
            'alertRuleId': rule_id,
            'title': 'To Delete',
            'message': 'Delete me',
            'notificationMethod': 'PUSH',
            'status': 'PENDING',
        }

        create_response = client.post(
            '/alerts/notifications', json=notification_payload
        )
        notification_id = create_response.json()['id']

        # Delete it
        response = client.delete(f'/alerts/notifications/{notification_id}')
        assert response.status_code == 200
        assert response.json()['message'] == 'Alert notification deleted successfully'

        # Verify it's gone
        get_response = client.get(f'/alerts/notifications/{notification_id}')
        assert get_response.status_code == 404


class TestUtilityEndpoints(TestUserSetup):
    """Test utility endpoints"""

    def test_get_notifications_for_rule(self):
        """Test getting notifications for a specific rule"""
        # Create a rule
        rule_payload = {
            'userId': self.user_id,
            'name': 'Test Rule',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Create notifications for this rule
        notifications = [
            {
                'userId': self.user_id,
                'alertRuleId': rule_id,
                'title': 'Notification 1',
                'message': 'First notification',
                'notificationMethod': 'EMAIL',
                'status': 'SENT',
            },
            {
                'userId': self.user_id,
                'alertRuleId': rule_id,
                'title': 'Notification 2',
                'message': 'Second notification',
                'notificationMethod': 'SMS',
                'status': 'PENDING',
            },
        ]

        for notification in notifications:
            client.post('/alerts/notifications', json=notification)

        # Get notifications for the rule
        response = client.get(f'/alerts/rules/{rule_id}/notifications')
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2
        assert all(notification['alertRuleId'] == rule_id for notification in data)

    def test_trigger_alert_rule(self):
        """Test manually triggering an alert rule"""
        # Create an active rule
        rule_payload = {
            'userId': self.user_id,
            'name': 'Test Rule',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
            'isActive': True,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Trigger it
        response = client.post(f'/alerts/rules/{rule_id}/trigger')
        assert response.status_code == 200

        data = response.json()
        assert data['message'] == 'Alert rule triggered successfully'
        assert data['triggerCount'] == 1

        # Verify the rule was updated
        rule_response = client.get(f'/alerts/rules/{rule_id}')
        rule_data = rule_response.json()
        assert rule_data['triggerCount'] == 1
        assert rule_data['lastTriggered'] is not None

    def test_trigger_inactive_rule(self):
        """Test triggering an inactive rule"""
        # Create an inactive rule
        rule_payload = {
            'userId': self.user_id,
            'name': 'Inactive Rule',
            'alertType': 'AMOUNT_THRESHOLD',
            'amountThreshold': 100.0,
            'isActive': False,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Try to trigger it
        response = client.post(f'/alerts/rules/{rule_id}/trigger')
        assert response.status_code == 400
        assert 'Alert rule is not active' in response.json()['detail']
