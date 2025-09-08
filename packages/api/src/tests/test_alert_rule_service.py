"""Test cases for AlertRuleService"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from db.models import AlertNotification, AlertRule, AlertType, Transaction

from services.alert_rule_service import AlertRuleService


class TestAlertRuleService:
    """Test suite for AlertRuleService"""

    @pytest.fixture
    def alert_rule_service(self):
        """Create an AlertRuleService instance for testing"""
        return AlertRuleService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        session = AsyncMock()
        return session

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction object"""
        transaction = MagicMock(spec=Transaction)
        transaction.id = 'tx-123'
        transaction.user_id = 'user-456'
        transaction.amount = Decimal('150.00')
        transaction.currency = 'USD'
        transaction.merchant_name = 'Test Store'
        transaction.merchant_category = 'Retail'
        transaction.transaction_date = datetime(2024, 1, 15, 14, 30, 0)
        transaction.trans_num = 'trans-789'
        transaction.__dict__ = {
            'id': transaction.id,
            'user_id': transaction.user_id,
            'amount': transaction.amount,
            'currency': transaction.currency,
            'merchant_name': transaction.merchant_name,
            'merchant_category': transaction.merchant_category,
            'transaction_date': transaction.transaction_date,
            'trans_num': transaction.trans_num,
        }
        return transaction

    @pytest.fixture
    def sample_alert_rule(self):
        """Create a sample alert rule object"""
        rule = MagicMock(spec=AlertRule)
        rule.id = 'rule-123'
        rule.user_id = 'user-456'
        rule.name = 'Large transaction alert'
        rule.natural_language_query = 'Alert me when transactions exceed $100'
        rule.is_active = True
        rule.trigger_count = 5
        rule.alert_type = AlertType.AMOUNT_THRESHOLD
        return rule

    @pytest.fixture
    def inactive_alert_rule(self):
        """Create an inactive alert rule object"""
        rule = MagicMock(spec=AlertRule)
        rule.id = 'rule-456'
        rule.user_id = 'user-456'
        rule.name = 'Inactive alert'
        rule.natural_language_query = 'Alert me for dining expenses'
        rule.is_active = False
        rule.trigger_count = 0
        return rule

    @pytest.mark.asyncio
    async def test_validate_alert_rule_success_with_real_transaction(
        self, alert_rule_service, mock_session, sample_transaction
    ):
        """Test successful validation of alert rule with a real transaction"""
        # Arrange
        rule_text = 'Alert me when transactions exceed $100'
        user_id = 'user-456'

        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM parsing to return valid result
            with patch.object(AlertRuleService, 'parse_nl_rule_with_llm') as mock_parse:
                mock_parse.return_value = {
                    'valid_sql': True,
                    'alert_text': rule_text,
                    'sql_query': 'SELECT * FROM transactions WHERE amount > 100',
                }

                # Act
                result = await alert_rule_service.validate_alert_rule(
                    rule_text, user_id, mock_session
                )

                # Assert
                assert result['status'] == 'valid'
                assert result['message'] == 'Alert rule validated successfully'
                assert result['user_id'] == user_id
                assert 'validation_timestamp' in result
                assert result['alert_text'] == rule_text
                assert 'sql_query' in result
                assert result['transaction_used'] == sample_transaction.__dict__

    @pytest.mark.asyncio
    async def test_validate_alert_rule_success_with_dummy_transaction(
        self, alert_rule_service, mock_session
    ):
        """Test successful validation of alert rule with dummy transaction (no real transaction found)"""
        # Arrange
        rule_text = 'Alert me when transactions exceed $100'
        user_id = 'user-456'

        # Mock the transaction service to return None (no transaction found)
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=None,
        ):
            # Mock the dummy transaction
            dummy_transaction = {'user_id': user_id, 'amount': 100.0}
            with patch.object(
                alert_rule_service.transaction_service,
                'get_dummy_transaction',
                return_value=dummy_transaction,
            ):
                # Mock the LLM parsing to return valid result
                with patch.object(
                    AlertRuleService, 'parse_nl_rule_with_llm'
                ) as mock_parse:
                    mock_parse.return_value = {
                        'valid_sql': True,
                        'alert_text': rule_text,
                        'sql_query': 'SELECT * FROM transactions WHERE amount > 100',
                    }

                    # Act
                    result = await alert_rule_service.validate_alert_rule(
                        rule_text, user_id, mock_session
                    )

                    # Assert
                    assert result['status'] == 'valid'
                    assert result['transaction_used'] == dummy_transaction

    @pytest.mark.asyncio
    async def test_validate_alert_rule_invalid_sql(
        self, alert_rule_service, mock_session, sample_transaction
    ):
        """Test validation of alert rule that produces invalid SQL"""
        # Arrange
        rule_text = 'Invalid rule text'
        user_id = 'user-456'

        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM parsing to return invalid result
            with patch.object(AlertRuleService, 'parse_nl_rule_with_llm') as mock_parse:
                mock_parse.return_value = {'valid_sql': False, 'alert_text': rule_text}

                # Act
                result = await alert_rule_service.validate_alert_rule(
                    rule_text, user_id, mock_session
                )

                # Assert
                assert result['status'] == 'invalid'
                assert result['message'] == 'Rule could not be parsed or validated'
                assert result['error'] == 'LLM could not parse rule structure'
                assert result['user_id'] == user_id

    @pytest.mark.asyncio
    async def test_validate_alert_rule_llm_error(
        self, alert_rule_service, mock_session, sample_transaction
    ):
        """Test validation when LLM throws an error"""
        # Arrange
        rule_text = 'Alert me when transactions exceed $100'
        user_id = 'user-456'

        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM parsing to raise an exception
            with patch.object(AlertRuleService, 'parse_nl_rule_with_llm') as mock_parse:
                mock_parse.side_effect = Exception('LLM service unavailable')

                # Act
                result = await alert_rule_service.validate_alert_rule(
                    rule_text, user_id, mock_session
                )

                # Assert
                assert result['status'] == 'error'
                assert 'Validation failed' in result['message']
                assert result['error'] == 'LLM service unavailable'

    @pytest.mark.asyncio
    async def test_trigger_alert_rule_success(
        self, alert_rule_service, mock_session, sample_alert_rule, sample_transaction
    ):
        """Test successful triggering of an alert rule"""
        # Arrange
        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM generation to return trigger result
            with patch.object(
                AlertRuleService, 'generate_alert_with_llm'
            ) as mock_generate:
                mock_generate.return_value = {
                    'should_trigger': True,
                    'message': 'Large transaction detected: $150.00',
                }

                # Mock session operations
                mock_session.add = MagicMock()
                mock_session.commit = AsyncMock()

                # Act
                result = await alert_rule_service.trigger_alert_rule(
                    sample_alert_rule, mock_session
                )

                # Assert
                assert result['status'] == 'triggered'
                assert result['message'] == 'Alert rule triggered successfully'
                assert result['trigger_count'] == sample_alert_rule.trigger_count + 1
                assert result['transaction_id'] == sample_transaction.trans_num
                assert 'notification_id' in result
                assert 'rule_evaluation' in result

                # Verify database operations
                mock_session.add.assert_called_once()
                mock_session.execute.assert_called_once()
                mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_alert_rule_not_triggered(
        self, alert_rule_service, mock_session, sample_alert_rule, sample_transaction
    ):
        """Test triggering alert rule when conditions are not met"""
        # Arrange
        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM generation to return no trigger result
            with patch.object(
                AlertRuleService, 'generate_alert_with_llm'
            ) as mock_generate:
                mock_generate.return_value = {
                    'should_trigger': False,
                    'message': 'Transaction amount is within normal range',
                }

                # Act
                result = await alert_rule_service.trigger_alert_rule(
                    sample_alert_rule, mock_session
                )

                # Assert
                assert result['status'] == 'not_triggered'
                assert result['message'] == 'Rule evaluated but alert not triggered'
                assert result['transaction_id'] == sample_transaction.trans_num
                assert 'rule_evaluation' in result

    @pytest.mark.asyncio
    async def test_trigger_alert_rule_inactive_rule(
        self, alert_rule_service, mock_session, inactive_alert_rule
    ):
        """Test triggering an inactive alert rule"""
        # Act & Assert
        with pytest.raises(ValueError, match='Alert rule is not active'):
            await alert_rule_service.trigger_alert_rule(
                inactive_alert_rule, mock_session
            )

    @pytest.mark.asyncio
    async def test_trigger_alert_rule_no_transaction(
        self, alert_rule_service, mock_session, sample_alert_rule
    ):
        """Test triggering alert rule when user has no transactions"""
        # Arrange
        # Mock the transaction service to return None
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=None,
        ):
            # Act & Assert
            with pytest.raises(ValueError, match='No transaction found for user'):
                await alert_rule_service.trigger_alert_rule(
                    sample_alert_rule, mock_session
                )

    @pytest.mark.asyncio
    async def test_trigger_alert_rule_llm_error(
        self, alert_rule_service, mock_session, sample_alert_rule, sample_transaction
    ):
        """Test triggering alert rule when LLM generation fails"""
        # Arrange
        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM generation to raise an exception
            with patch.object(
                AlertRuleService, 'generate_alert_with_llm'
            ) as mock_generate:
                mock_generate.side_effect = Exception('LLM generation failed')

                # Act
                result = await alert_rule_service.trigger_alert_rule(
                    sample_alert_rule, mock_session
                )

                # Assert
                assert result['status'] == 'error'
                assert 'Alert generation failed' in result['message']
                assert result['error'] == 'LLM generation failed'
                assert result['transaction_id'] == sample_transaction.trans_num

    def test_parse_nl_rule_with_llm_success(self):
        """Test successful parsing of natural language rule with LLM"""
        # Arrange
        alert_text = 'Alert me when transactions exceed $100'
        transaction = {'amount': 150.0, 'merchant': 'Test Store'}

        with patch('services.alert_rule_service.parse_alert_graph') as mock_graph:
            mock_graph.invoke.return_value = {
                'valid_sql': True,
                'alert_text': alert_text,
                'sql_query': 'SELECT * FROM transactions WHERE amount > 100',
            }

            # Act
            result = AlertRuleService.parse_nl_rule_with_llm(alert_text, transaction)

            # Assert
            assert result['valid_sql'] is True
            assert result['alert_text'] == alert_text
            mock_graph.invoke.assert_called_once_with(
                {'transaction': transaction, 'alert_text': alert_text}
            )

    def test_parse_nl_rule_with_llm_error(self):
        """Test parsing of natural language rule when LLM fails"""
        # Arrange
        alert_text = 'Invalid rule'
        transaction = {'amount': 150.0}

        with patch('services.alert_rule_service.parse_alert_graph') as mock_graph:
            mock_graph.invoke.side_effect = Exception('LLM parsing failed')

            # Act & Assert
            with pytest.raises(Exception, match='LLM parsing failed'):
                AlertRuleService.parse_nl_rule_with_llm(alert_text, transaction)

    def test_generate_alert_with_llm_success(self):
        """Test successful generation of alert with LLM"""
        # Arrange
        alert_text = 'Alert me when transactions exceed $100'
        transaction = {'amount': 150.0, 'merchant': 'Test Store'}

        with patch('services.alert_rule_service.generate_alert_graph') as mock_graph:
            mock_graph.invoke.return_value = {
                'should_trigger': True,
                'message': 'Large transaction detected: $150.00',
            }

            # Act
            result = AlertRuleService.generate_alert_with_llm(alert_text, transaction)

            # Assert
            assert result['should_trigger'] is True
            assert 'Large transaction detected' in result['message']
            mock_graph.invoke.assert_called_once_with(
                {'transaction': transaction, 'alert_text': alert_text}
            )

    def test_generate_alert_with_llm_error(self):
        """Test generation of alert when LLM fails"""
        # Arrange
        alert_text = 'Alert me when transactions exceed $100'
        transaction = {'amount': 150.0}

        with patch('services.alert_rule_service.generate_alert_graph') as mock_graph:
            mock_graph.invoke.side_effect = Exception('LLM generation failed')

            # Act & Assert
            with pytest.raises(Exception, match='LLM generation failed'):
                AlertRuleService.generate_alert_with_llm(alert_text, transaction)

    @pytest.mark.asyncio
    async def test_validate_alert_rule_none_result_from_llm(
        self, alert_rule_service, mock_session, sample_transaction
    ):
        """Test validation when LLM returns None"""
        # Arrange
        rule_text = 'Alert me when transactions exceed $100'
        user_id = 'user-456'

        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM parsing to return None
            with patch.object(AlertRuleService, 'parse_nl_rule_with_llm') as mock_parse:
                mock_parse.return_value = None

                # Act
                result = await alert_rule_service.validate_alert_rule(
                    rule_text, user_id, mock_session
                )

                # Assert
                assert result['status'] == 'invalid'
                assert result['message'] == 'Rule could not be parsed or validated'

    @pytest.mark.asyncio
    async def test_trigger_alert_rule_none_result_from_llm(
        self, alert_rule_service, mock_session, sample_alert_rule, sample_transaction
    ):
        """Test triggering when LLM returns None"""
        # Arrange
        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM generation to return None
            with patch.object(
                AlertRuleService, 'generate_alert_with_llm'
            ) as mock_generate:
                mock_generate.return_value = None

                # Act
                result = await alert_rule_service.trigger_alert_rule(
                    sample_alert_rule, mock_session
                )

                # Assert
                assert result['status'] == 'not_triggered'
                assert result['message'] == 'Rule evaluated but alert not triggered'

    @pytest.mark.asyncio
    async def test_trigger_alert_rule_creates_correct_notification(
        self, alert_rule_service, mock_session, sample_alert_rule, sample_transaction
    ):
        """Test that triggering creates notification with correct data"""
        # Arrange
        # Mock the transaction service to return a transaction
        with patch.object(
            alert_rule_service.transaction_service,
            'get_latest_transaction',
            return_value=sample_transaction,
        ):
            # Mock the LLM generation to return trigger result
            with patch.object(
                AlertRuleService, 'generate_alert_with_llm'
            ) as mock_generate:
                mock_generate.return_value = {
                    'should_trigger': True,
                    'message': 'Custom alert message',
                }

                # Mock session operations
                mock_session.add = MagicMock()
                mock_session.commit = AsyncMock()

                # Act
                result = await alert_rule_service.trigger_alert_rule(
                    sample_alert_rule, mock_session
                )

                # Assert
                # Verify notification was created with correct data
                call_args = mock_session.add.call_args[0][
                    0
                ]  # Get the notification object
                assert isinstance(call_args, AlertNotification)
                assert call_args.user_id == sample_alert_rule.user_id
                assert call_args.alert_rule_id == sample_alert_rule.id
                assert call_args.transaction_id == sample_transaction.trans_num
                assert call_args.title == f'Alert: {sample_alert_rule.name}'
                assert call_args.message == 'Custom alert message'
                assert call_args.notification_method == 'system'
                assert call_args.status == 'sent'
