"""Alert monitoring service for continuous transaction monitoring"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import List

from db import get_db
from db.models import (
    AlertNotification,
    AlertRule,
    NotificationMethod,
    NotificationStatus,
    Transaction,
    User,
)
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .alert_rule_service import AlertRuleService
from .notifications import Context, SmtpStrategy, NoopStrategy

logger = logging.getLogger(__name__)


class AlertMonitorService:
    """Service for continuously monitoring transactions against alert rules"""

    def __init__(self):
        self.alert_rule_service = AlertRuleService()
        self._running = False

    async def start_monitoring(self, check_interval: int = 30):
        """Start the continuous monitoring process"""
        self._running = True
        logger.info("Starting alert monitoring service...")

        while self._running:
            try:
                await self._check_transactions_against_rules()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(check_interval)

    def stop_monitoring(self):
        """Stop the monitoring process"""
        self._running = False
        logger.info("Stopping alert monitoring service...")

    async def _check_transactions_against_rules(self):
        """Check recent transactions against all active alert rules"""
        async for session in get_db():
            try:
                # Get all active alert rules
                result = await session.execute(
                    select(AlertRule).where(AlertRule.is_active == True)
                )
                active_rules = result.scalars().all()

                if not active_rules:
                    logger.debug("No active alert rules found")
                    return

                logger.info(f"Checking {len(active_rules)} active alert rules")

                # Process each rule
                for rule in active_rules:
                    try:
                        await self._process_rule_for_new_transactions(rule, session)
                    except Exception as e:
                        logger.error(f"Error processing rule {rule.id}: {e}")

                await session.commit()

            except Exception as e:
                logger.error(f"Error in transaction checking: {e}")
                await session.rollback()
            finally:
                await session.close()
                break  # Exit the async generator

    async def _process_rule_for_new_transactions(self, rule: AlertRule, session: AsyncSession):
        """Process a specific rule against new transactions"""

        # Get transactions since last rule trigger or creation
        since_time = rule.last_triggered or rule.created_at

        result = await session.execute(
            select(Transaction)
            .where(Transaction.user_id == rule.user_id)
            .where(Transaction.transaction_date > since_time)
            .order_by(Transaction.transaction_date.desc())
        )

        new_transactions = result.scalars().all()

        if not new_transactions:
            logger.debug(f"No new transactions for rule {rule.id}")
            return

        logger.info(f"Found {len(new_transactions)} new transactions for rule {rule.id}")

        # Check each transaction against the rule
        for transaction in new_transactions:
            try:
                await self._evaluate_transaction_against_rule(transaction, rule, session)
            except Exception as e:
                logger.error(f"Error evaluating transaction {transaction.id} against rule {rule.id}: {e}")

    async def _evaluate_transaction_against_rule(
        self, transaction: Transaction, rule: AlertRule, session: AsyncSession
    ):
        """Evaluate a specific transaction against an alert rule"""

        # Use the stored SQL query if available, otherwise generate it
        if rule.sql_query:
            sql_query = rule.sql_query
            logger.debug(f"Using stored SQL query for rule {rule.id}")
        else:
            # Generate SQL query using LLM
            logger.debug(f"Generating SQL query for rule {rule.id}")
            from .alerts.agents.alert_parser import parse_alert_to_sql_with_context

            transaction_dict = {
                'user_id': transaction.user_id,
                'transaction_date': str(transaction.transaction_date),
                'amount': float(transaction.amount),
                'merchant_name': transaction.merchant_name,
                'merchant_category': transaction.merchant_category,
                'description': transaction.description,
                'currency': transaction.currency,
                'credit_card_num': transaction.credit_card_num,
                'merchant_city': transaction.merchant_city,
                'merchant_state': transaction.merchant_state,
                'merchant_country': transaction.merchant_country,
                'trans_num': transaction.trans_num,
                'authorization_code': transaction.authorization_code
            }

            sql_query = parse_alert_to_sql_with_context(transaction_dict, rule.natural_language_query)

            # Store the generated SQL query for future use
            await session.execute(
                update(AlertRule)
                .where(AlertRule.id == rule.id)
                .values(sql_query=sql_query)
            )

        # Execute the SQL query
        from .alerts.agents.sql_executor import execute_sql

        query_result = execute_sql(sql_query)

        # Check if alert should be triggered
        alert_triggered = self._should_trigger_alert(query_result)

        if alert_triggered:
            await self._create_and_send_notification(transaction, rule, query_result, session)

    def _should_trigger_alert(self, query_result: str) -> bool:
        """Determine if an alert should be triggered based on query result"""
        try:
            # Check if query returned results and doesn't indicate error
            return (
                query_result
                and not query_result.startswith('SQL Error')
                and query_result != '[]'
                and query_result.strip() != ''
            )
        except Exception:
            return False

    async def _create_and_send_notification(
        self, transaction: Transaction, rule: AlertRule, query_result: str, session: AsyncSession
    ):
        """Create and send a notification for a triggered alert"""

        # Generate alert message using LLM
        from .alerts.agents.generate_alert_message import generate_alert_message

        context = {
            'transaction': transaction.__dict__,
            'query_result': query_result,
            'alert_text': rule.natural_language_query,
            'alert_rule': {
                'name': rule.name,
                'description': rule.description,
                'alert_type': str(rule.alert_type)
            }
        }

        try:
            alert_message = generate_alert_message(context)
        except Exception as e:
            logger.error(f"Error generating alert message: {e}")
            alert_message = f"Alert triggered: {rule.name} - Transaction amount: ${transaction.amount}"

        # Create notification
        notification = AlertNotification(
            id=str(uuid.uuid4()),
            user_id=rule.user_id,
            alert_rule_id=rule.id,
            transaction_id=transaction.id,
            title=f"Alert: {rule.name}",
            message=alert_message,
            notification_method=NotificationMethod.EMAIL,  # Default to email
            status=NotificationStatus.PENDING,
        )

        # Send notification based on rule's notification methods
        notification_methods = rule.notification_methods or [NotificationMethod.EMAIL]

        for method in notification_methods:
            try:
                notification_copy = AlertNotification(
                    id=str(uuid.uuid4()),
                    user_id=rule.user_id,
                    alert_rule_id=rule.id,
                    transaction_id=transaction.id,
                    title=f"Alert: {rule.name}",
                    message=alert_message,
                    notification_method=method,
                    status=NotificationStatus.PENDING,
                )

                # Send notification
                if method == NotificationMethod.EMAIL:
                    strategy = SmtpStrategy()
                else:
                    strategy = NoopStrategy()  # For now, only email is implemented

                ctx = Context(strategy)
                sent_notification = await ctx.send_notification(notification_copy, session)

                session.add(sent_notification)
                logger.info(f"Notification sent via {method} for alert {rule.id}")

            except Exception as e:
                logger.error(f"Error sending notification via {method}: {e}")

        # Update rule trigger count and last triggered time
        await session.execute(
            update(AlertRule)
            .where(AlertRule.id == rule.id)
            .values(
                trigger_count=rule.trigger_count + 1,
                last_triggered=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )

        logger.info(f"Alert {rule.id} triggered for transaction {transaction.id}")


# Global monitor instance
alert_monitor = AlertMonitorService()


async def start_alert_monitoring():
    """Start the alert monitoring service"""
    await alert_monitor.start_monitoring()


def stop_alert_monitoring():
    """Stop the alert monitoring service"""
    alert_monitor.stop_monitoring()