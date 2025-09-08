"""
Kafka consumer service for processing transaction messages from ingestion service
"""

import asyncio
import json
import logging
import threading
import uuid
from datetime import datetime, time
from typing import Any

from db import get_db
from db.models import Transaction, TransactionStatus, TransactionType, User
from kafka import KafkaConsumer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class TransactionKafkaConsumer:
    """Kafka consumer for processing transaction messages from ingestion service"""

    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9092',
        topic: str = 'transactions',
        group_id: str = 'transaction-processor',
        auto_offset_reset: str = 'earliest',
        event_loop: asyncio.AbstractEventLoop = None,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.event_loop = event_loop
        self.consumer: KafkaConsumer | None = None
        self.running = False
        self.thread: threading.Thread | None = None

    def start(self):
        """Start the Kafka consumer in a separate thread"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=False,  # Manual offset commits for safety
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            )

            self.running = True
            self.thread = threading.Thread(target=self._consume_messages, daemon=True)
            self.thread.start()

            logger.info(f'Kafka consumer started for topic: {self.topic}')

        except Exception as e:
            logger.error(f'Failed to start Kafka consumer: {e}')
            raise

    def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info('Kafka consumer stopped')

    def _consume_messages(self):
        """Consume messages from Kafka topic in a separate thread"""
        try:
            for message in self.consumer:
                if not self.running:
                    break

                try:
                    if self.event_loop:
                        future = asyncio.run_coroutine_threadsafe(
                            self._process_transaction_message(message), self.event_loop
                        )
                        future.result(timeout=30)
                    else:
                        asyncio.run(self._process_transaction_message(message))

                except Exception as e:
                    logger.error(f'Error processing message: {e}')
                    # Don't commit offset on error - message will be reprocessed
                    continue

        except Exception as e:
            logger.error(f'Error in message consumption: {e}')
            raise

    async def _process_transaction_message(self, message):
        """Process a single transaction message from ingestion service"""
        try:
            logger.info(f'Processing transaction message: {message.value}')

            # Transform ingestion service format to our database format
            transaction_data = self._transform_ingestion_format(message.value)

            # Get database session
            async for session in get_db():
                try:
                    # Check if transaction already exists (using a composite key)
                    existing_transaction = await self._check_existing_transaction(
                        session, transaction_data
                    )

                    if existing_transaction:
                        logger.info('Transaction already exists, skipping')
                        # Commit offset even for duplicate messages to avoid reprocessing
                        self.consumer.commit()
                        return

                    # Validate user and credit card exist
                    await self._validate_user_and_card(session, transaction_data)

                    # Create transaction
                    transaction = await self._create_transaction(
                        session, transaction_data
                    )

                    logger.info(f'Successfully processed transaction: {transaction.id}')

                    # TODO: Trigger alert evaluation here
                    # await self._evaluate_alerts(transaction)

                    # Commit offset only after successful processing
                    self.consumer.commit()
                    logger.info(
                        f'Committed offset for message at partition {message.partition}, offset {message.offset}'
                    )

                except Exception as e:
                    logger.error(f'Database error processing transaction: {e}')
                    await session.rollback()
                    # Don't commit offset on error - message will be reprocessed
                    raise
                finally:
                    await session.close()

        except Exception as e:
            logger.error(f'Failed to process transaction message: {e}')
            # Don't commit offset on error - message will be reprocessed
            raise

    def _transform_ingestion_format(
        self, message_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Transform ingestion service format to our database format"""
        # Validate required date fields
        required_date_fields = ['year', 'month', 'day', 'time']
        for field in required_date_fields:
            if field not in message_data:
                raise ValueError(f'Missing required date field: {field}')

        # Extract time components
        time_obj = message_data.get('time')
        if isinstance(time_obj, str):
            # Parse time string like "14:30:00" using robust ISO format parsing
            try:
                transaction_time = time.fromisoformat(time_obj)
            except ValueError as ve:
                raise ValueError(
                    f'Invalid time format: {time_obj}. Expected HH:MM:SS or HH:MM'
                ) from ve
        else:
            transaction_time = time_obj

        # Create transaction date from year, month, day
        year = message_data['year']
        month = message_data['month']
        day = message_data['day']

        # Combine date and time - datetime constructor handles all validation
        try:
            transaction_date = datetime.combine(
                datetime(year, month, day).date(), transaction_time
            )
        except ValueError as e:
            raise ValueError(
                f'Invalid date: year={year}, month={month}, day={day}, time={time_obj}. {str(e)}'
            ) from e

        # Generate a unique ID for the transaction
        transaction_id = str(uuid.uuid4())

        # Transform to our database format
        transformed_data = {
            'id': transaction_id,
            'user_id': str(message_data.get('user')),  # Convert to string
            'credit_card_num': str(message_data.get('card')),  # Convert to string
            'amount': float(message_data.get('amount', 0)),
            'currency': 'USD',  # Default currency
            'description': f'Transaction at {message_data.get("merchant_id", "Unknown Merchant")}',
            'merchant_name': str(message_data.get('merchant_id', 'Unknown Merchant')),
            'merchant_category': str(message_data.get('mcc', 'UNKNOWN')),
            'transaction_date': transaction_date.isoformat(),
            'transaction_type': TransactionType.PURCHASE.value,
            'status': TransactionStatus.PENDING.value,
            'merchant_latitude': message_data.get('merchant_latitude'),
            'merchant_longitude': message_data.get('merchant_longitude'),
            'merchant_zipcode': message_data.get('merchant_zipcode'),
            'merchant_city': message_data.get('merchant_city'),
            'merchant_state': message_data.get('merchant_state'),
            'merchant_country': message_data.get('merchant_country'),  # Default country
            'authorization_code': None,
            'trans_num': message_data.get('trans_num'),
            # Additional fields from ingestion service
            'useChip': message_data.get('use_chip'),
            'zipCode': message_data.get('zip'),
            'isFraud': message_data.get('is_fraud', False),
            'errors': message_data.get('errors'),
        }

        return transformed_data

    async def _check_existing_transaction(
        self, session: AsyncSession, transaction_data: dict[str, Any]
    ) -> Transaction | None:
        """Check if a transaction already exists based on user, card, amount, and date"""
        # Create a composite key check
        result = await session.execute(
            select(Transaction).where(
                Transaction.user_id == transaction_data['user_id'],
                Transaction.credit_card_num == transaction_data['credit_card_num'],
                Transaction.amount == transaction_data['amount'],
                Transaction.transaction_date
                == datetime.fromisoformat(transaction_data['transaction_date']),
            )
        )
        return result.scalar_one_or_none()

    async def _validate_user_and_card(
        self, session: AsyncSession, transaction_data: dict[str, Any]
    ):
        """Validate that user and credit card exist"""
        # Check user exists
        user_result = await session.execute(
            select(User).where(User.id == transaction_data['user_id'])
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError(f'User not found: {transaction_data["user_id"]}')

        # Check credit card exists
        # card_result = await session.execute(
        #     select(CreditCard).where(CreditCard.id == transaction_data['credit_card_num'])
        # )
        # card = card_result.scalar_one_or_none()
        # if not card:
        #     raise ValueError(
        #         f'Credit card not found: {transaction_data["credit_card_num"]}'
        #     )

        # Verify credit card belongs to user
        # if card.user_id != transaction_data['user_id']:
        #     raise ValueError(
        #         f'Credit card {transaction_data["credit_card_num"]} does not belong to user {transaction_data["user_id"]}'
        #     )

    async def _create_transaction(
        self, session: AsyncSession, transaction_data: dict[str, Any]
    ) -> Transaction:
        """Create a new transaction in the database"""
        # Parse transaction date
        if isinstance(transaction_data['transaction_date'], str):
            transaction_date = datetime.fromisoformat(
                transaction_data['transaction_date']
            )
        else:
            transaction_date = transaction_data['transaction_date']

        transaction = Transaction(
            id=transaction_data['id'],
            user_id=transaction_data['user_id'],
            credit_card_num=transaction_data['credit_card_num'],
            amount=transaction_data['amount'],
            currency=transaction_data['currency'],
            description=transaction_data['description'],
            merchant_name=transaction_data['merchant_name'],
            merchant_category=transaction_data['merchant_category'],
            transaction_date=transaction_date,
            transaction_type=TransactionType(transaction_data['transaction_type']),
            merchant_latitude=transaction_data.get('merchant_latitude'),
            merchant_longitude=transaction_data.get('merchant_longitude'),
            merchant_zipcode=transaction_data.get('merchant_zipcode'),
            merchant_city=transaction_data.get('merchant_city'),
            merchant_state=transaction_data.get('merchant_state'),
            merchant_country=transaction_data.get('merchant_country'),
            status=TransactionStatus(transaction_data['status']),
            authorization_code=transaction_data.get('authorization_code'),
            trans_num=transaction_data.get('trans_num'),
        )

        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)

        return transaction

    async def _evaluate_alerts(self, transaction: Transaction):
        """Evaluate alerts for the transaction (placeholder for future implementation)"""
        # TODO: Implement alert evaluation logic
        logger.info(f'Alert evaluation triggered for transaction: {transaction.id}')
        pass


# Global consumer instance
transaction_consumer: TransactionKafkaConsumer | None = None


def start_transaction_consumer(
    bootstrap_servers: str = 'localhost:9092',
    topic: str = 'transactions',
    group_id: str = 'transaction-processor',
    event_loop: asyncio.AbstractEventLoop = None,
):
    """Start the transaction consumer"""
    global transaction_consumer

    if transaction_consumer is None:
        transaction_consumer = TransactionKafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            topic=topic,
            group_id=group_id,
            event_loop=event_loop,
        )

    transaction_consumer.start()


def stop_transaction_consumer():
    """Stop the transaction consumer"""
    global transaction_consumer

    if transaction_consumer:
        transaction_consumer.stop()
        transaction_consumer = None
