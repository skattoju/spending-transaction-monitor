#!/usr/bin/env python3
"""
Test script for Kafka consumer setup
"""

import json
import logging
import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from kafka import KafkaProducer

from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_kafka_connection():
    """Test basic Kafka connectivity"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
        )
        logger.info('✅ Successfully connected to Kafka')
        producer.close()
        return True
    except Exception as e:
        logger.error(f'❌ Failed to connect to Kafka: {e}')
        return False


def send_test_message():
    """Send a test message to Kafka in ingestion service format"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
        )

        # Create a test transaction message in ingestion service format
        test_message = {
            'user': 123,
            'card': 456,
            'year': datetime.now().year,
            'month': datetime.now().month,
            'day': datetime.now().day,
            'time': datetime.now().strftime('%H:%M:%S'),
            'amount': 99.99,
            'use_chip': 'Chip Transaction',
            'merchant_id': 789,
            'merchant_city': 'Test City',
            'merchant_state': 'CA',
            'zip': '12345',
            'mcc': 5411,  # Grocery stores
            'errors': None,
            'is_fraud': False,
        }

        future = producer.send(settings.KAFKA_TRANSACTIONS_TOPIC, test_message)
        record_metadata = future.get(timeout=10)
        logger.info(
            f"✅ Successfully sent test message to topic '{record_metadata.topic}' at partition {record_metadata.partition} with offset {record_metadata.offset}"
        )
        producer.close()
        return True
    except Exception as e:
        logger.error(f'❌ Failed to send test message: {e}')
        return False


def main():
    """Main test function"""
    logger.info('🧪 Testing Kafka setup...')
    logger.info(f'📡 Using Kafka bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}')
    logger.info(f'📨 Using Kafka topic: {settings.KAFKA_TRANSACTIONS_TOPIC}')

    # Test 1: Kafka connection
    logger.info('\n1. Testing Kafka connection...')
    kafka_ok = test_kafka_connection()

    if not kafka_ok:
        logger.error('❌ Kafka connection failed. Please ensure Kafka is running.')
        logger.info(
            '💡 Start Kafka with: docker-compose -f docker-compose.kafka.yml up -d'
        )
        return

    # Test 2: Send test message
    logger.info('\n2. Testing message sending...')
    message_ok = send_test_message()

    if message_ok:
        logger.info('\n✅ All tests passed!')
        logger.info(
            '💡 Check your API logs to see if the consumer processed the message'
        )
        logger.info('💡 Check the database to see if the transaction was stored')
    else:
        logger.error('\n❌ Message sending failed')


if __name__ == '__main__':
    main()
