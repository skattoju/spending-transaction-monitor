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
            'first_name': 'Alert',
            'last_name': 'Tester',
            'phone_number': '+1-555-9999',
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
            'user_id': self.user_id,
            'name': 'High Amount Alert',
            'description': 'Alert for transactions over $1000',
            'is_active': True,
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 1000.0,
            'notification_methods': ['EMAIL', 'PUSH'],
        }

        response = client.post('/alerts/rules', json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['name'] == payload['name']
        assert data['alert_type'] == payload['alert_type']
        assert data['amount_threshold'] == payload['amount_threshold']
        assert data['is_active'] == payload['is_active']
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_create_alert_rule_invalid_user(self):
        """Test creating alert rule with non-existent user"""
        payload = {
            'user_id': 'non-existent-user',
            'name': 'Test Alert',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        response = client.post('/alerts/rules', json=payload)
        assert response.status_code == 404
        assert 'User not found' in response.json()['detail']

    def test_get_alert_rule_by_id(self):
        """Test getting a specific alert rule"""
        # First create a rule
        create_payload = {
            'user_id': self.user_id,
            'name': 'Test Rule',
            'alert_type': 'MERCHANT_CATEGORY',
            'merchant_category': 'RESTAURANTS',
        }

        create_response = client.post('/alerts/rules', json=create_payload)
        rule_id = create_response.json()['id']

        # Then get it by ID
        response = client.get(f'/alerts/rules/{rule_id}')
        assert response.status_code == 200

        data = response.json()
        assert data['id'] == rule_id
        assert data['name'] == create_payload['name']
        assert data['alert_type'] == create_payload['alert_type']

    def test_get_alert_rule_not_found(self):
        """Test getting non-existent alert rule"""
        response = client.get('/alerts/rules/non-existent-id')
        assert response.status_code == 404
        assert 'Alert rule not found' in response.json()['detail']

    def test_update_alert_rule(self):
        """Test updating an alert rule"""
        # First create a rule
        create_payload = {
            'user_id': self.user_id,
            'name': 'Original Name',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 500.0,
        }

        create_response = client.post('/alerts/rules', json=create_payload)
        rule_id = create_response.json()['id']

        # Then update it
        update_payload = {
            'name': 'Updated Name',
            'amount_threshold': 750.0,
            'is_active': False,
        }

        response = client.put(f'/alerts/rules/{rule_id}', json=update_payload)
        assert response.status_code == 200

        data = response.json()
        assert data['name'] == update_payload['name']
        assert data['amount_threshold'] == update_payload['amount_threshold']
        assert data['is_active'] == update_payload['is_active']

    def test_delete_alert_rule(self):
        """Test deleting an alert rule without notifications"""
        # First create a rule
        create_payload = {
            'user_id': self.user_id,
            'name': 'To Delete',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        create_response = client.post('/alerts/rules', json=create_payload)
        rule_id = create_response.json()['id']

        # Then delete it
        response = client.delete(f'/alerts/rules/{rule_id}')
        assert response.status_code == 200
        response_data = response.json()
        assert 'Alert rule deleted successfully' in response_data['message']
        assert (
            '0 associated notifications were also deleted' in response_data['message']
        )

        # Verify it's gone
        get_response = client.get(f'/alerts/rules/{rule_id}')
        assert get_response.status_code == 404

    def test_delete_alert_rule_with_notifications(self):
        """Test deleting an alert rule that has associated notifications"""
        # First create a rule
        rule_payload = {
            'user_id': self.user_id,
            'name': 'Rule with Notifications',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Create multiple notifications for this rule
        notifications = [
            {
                'user_id': self.user_id,
                'alert_rule_id': rule_id,
                'title': 'Notification 1',
                'message': 'First notification for this rule',
                'notification_method': 'EMAIL',
                'status': 'SENT',
            },
            {
                'user_id': self.user_id,
                'alert_rule_id': rule_id,
                'title': 'Notification 2',
                'message': 'Second notification for this rule',
                'notification_method': 'SMS',
                'status': 'PENDING',
            },
            {
                'user_id': self.user_id,
                'alert_rule_id': rule_id,
                'title': 'Notification 3',
                'message': 'Third notification for this rule',
                'notification_method': 'PUSH',
                'status': 'DELIVERED',
            },
        ]

        notification_ids = []
        for notification in notifications:
            response = client.post('/alerts/notifications', json=notification)
            if response.status_code == 200:
                notification_ids.append(response.json()['id'])

        # Verify notifications were created
        rule_notifications_response = client.get(
            f'/alerts/rules/{rule_id}/notifications'
        )
        assert rule_notifications_response.status_code == 200
        created_notifications = rule_notifications_response.json()
        assert len(created_notifications) == len(notification_ids)

        # Now delete the rule
        delete_response = client.delete(f'/alerts/rules/{rule_id}')
        assert delete_response.status_code == 200

        delete_data = delete_response.json()
        assert 'Alert rule deleted successfully' in delete_data['message']
        assert (
            f'{len(notification_ids)} associated notifications were also deleted'
            in delete_data['message']
        )

        # Verify the rule is gone
        get_rule_response = client.get(f'/alerts/rules/{rule_id}')
        assert get_rule_response.status_code == 404

        # Verify all notifications are gone
        for notification_id in notification_ids:
            get_notification_response = client.get(
                f'/alerts/notifications/{notification_id}'
            )
            assert get_notification_response.status_code == 404

        # Verify no notifications exist for the deleted rule
        rule_notifications_after_delete = client.get(
            f'/alerts/rules/{rule_id}/notifications'
        )
        assert rule_notifications_after_delete.status_code == 200
        assert rule_notifications_after_delete.json() == []

    def test_delete_nonexistent_alert_rule(self):
        """Test deleting a non-existent alert rule"""
        response = client.delete('/alerts/rules/non-existent-rule-id')
        assert response.status_code == 404
        assert 'Alert rule not found' in response.json()['detail']

    def test_filter_alert_rules(self):
        """Test filtering alert rules"""
        # Create multiple rules
        rules = [
            {
                'user_id': 'user-1',
                'name': 'Rule 1',
                'alert_type': 'AMOUNT_THRESHOLD',
                'amount_threshold': 100.0,
                'is_active': True,
            },
            {
                'user_id': 'user-2',
                'name': 'Rule 2',
                'alert_type': 'MERCHANT_CATEGORY',
                'merchant_category': 'SHOPPING',
                'is_active': False,
            },
        ]

        for rule in rules:
            client.post('/alerts/rules', json=rule)

        # Test filtering by user
        response = client.get('/alerts/rules?user_id=user-1')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['user_id'] == 'user-1'

        # Test filtering by active status
        response = client.get('/alerts/rules?is_active=true')
        assert response.status_code == 200
        data = response.json()
        assert all(rule['is_active'] for rule in data)


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
            'user_id': self.user_id,
            'name': 'Test Rule',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Then create a notification
        notification_payload = {
            'user_id': self.user_id,
            'alert_rule_id': rule_id,
            'title': 'High Transaction Alert',
            'message': 'Transaction over $100 detected',
            'notification_method': 'EMAIL',
            'status': 'PENDING',
        }

        response = client.post('/alerts/notifications', json=notification_payload)
        assert response.status_code == 200

        data = response.json()
        assert data['title'] == notification_payload['title']
        assert data['message'] == notification_payload['message']
        assert (
            data['notification_method'] == notification_payload['notification_method']
        )
        assert data['status'] == notification_payload['status']
        assert 'id' in data
        assert 'created_at' in data

    def test_create_notification_invalid_user(self):
        """Test creating notification with non-existent user"""
        payload = {
            'user_id': 'non-existent-user',
            'alert_rule_id': 'some-rule-id',
            'title': 'Test',
            'message': 'Test message',
            'notification_method': 'EMAIL',
            'status': 'PENDING',
        }

        response = client.post('/alerts/notifications', json=payload)
        assert response.status_code == 404
        assert 'User not found' in response.json()['detail']

    def test_create_notification_invalid_rule(self):
        """Test creating notification with non-existent alert rule"""
        payload = {
            'user_id': 'test-user-123',
            'alert_rule_id': 'non-existent-rule',
            'title': 'Test',
            'message': 'Test message',
            'notification_method': 'EMAIL',
            'status': 'PENDING',
        }

        response = client.post('/alerts/notifications', json=payload)
        assert response.status_code == 404
        assert 'Alert rule not found' in response.json()['detail']

    def test_get_notification_by_id(self):
        """Test getting a specific notification"""
        # Create rule and notification
        rule_payload = {
            'user_id': 'test-user-123',
            'name': 'Test Rule',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        notification_payload = {
            'user_id': 'test-user-123',
            'alert_rule_id': rule_id,
            'title': 'Test Notification',
            'message': 'Test message',
            'notification_method': 'SMS',
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
        assert (
            data['notification_method'] == notification_payload['notification_method']
        )

    def test_update_notification(self):
        """Test updating a notification"""
        # Create rule and notification
        rule_payload = {
            'user_id': 'test-user-123',
            'name': 'Test Rule',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        notification_payload = {
            'user_id': 'test-user-123',
            'alert_rule_id': rule_id,
            'title': 'Original Title',
            'message': 'Original message',
            'notification_method': 'EMAIL',
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
            'user_id': 'test-user-123',
            'name': 'Test Rule',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        notification_payload = {
            'user_id': 'test-user-123',
            'alert_rule_id': rule_id,
            'title': 'To Delete',
            'message': 'Delete me',
            'notification_method': 'PUSH',
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
            'user_id': self.user_id,
            'name': 'Test Rule',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Create notifications for this rule
        notifications = [
            {
                'user_id': self.user_id,
                'alert_rule_id': rule_id,
                'title': 'Notification 1',
                'message': 'First notification',
                'notification_method': 'EMAIL',
                'status': 'SENT',
            },
            {
                'user_id': self.user_id,
                'alert_rule_id': rule_id,
                'title': 'Notification 2',
                'message': 'Second notification',
                'notification_method': 'SMS',
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
        assert all(notification['alert_rule_id'] == rule_id for notification in data)

    def test_trigger_alert_rule(self):
        """Test manually triggering an alert rule"""
        # Create an active rule
        rule_payload = {
            'user_id': self.user_id,
            'name': 'Test Rule',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
            'is_active': True,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Trigger it
        response = client.post(f'/alerts/rules/{rule_id}/trigger')
        assert response.status_code == 200

        data = response.json()
        assert data['message'] == 'Alert rule triggered successfully'
        assert data['trigger_count'] == 1

        # Verify the rule was updated
        rule_response = client.get(f'/alerts/rules/{rule_id}')
        rule_data = rule_response.json()
        assert rule_data['trigger_count'] == 1
        assert rule_data['last_triggered'] is not None

    def test_trigger_inactive_rule(self):
        """Test triggering an inactive rule"""
        # Create an inactive rule
        rule_payload = {
            'user_id': self.user_id,
            'name': 'Inactive Rule',
            'alert_type': 'AMOUNT_THRESHOLD',
            'amount_threshold': 100.0,
            'is_active': False,
        }

        rule_response = client.post('/alerts/rules', json=rule_payload)
        rule_id = rule_response.json()['id']

        # Try to trigger it
        response = client.post(f'/alerts/rules/{rule_id}/trigger')
        assert response.status_code == 400
        assert 'Alert rule is not active' in response.json()['detail']
