"""
Ingestion Service
"""

import datetime
import os
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from .common.models import IncomingTransaction, Transaction


class APIClient:
    """Client for posting transactions to the API service"""

    def __init__(self):
        self.api_host = os.environ.get('API_HOST', 'localhost')
        self.api_port = os.environ.get('API_PORT', '8000')
        self.api_base_url = f'http://{self.api_host}:{self.api_port}'
        self.timeout = 30.0

    async def post_transaction(self, transaction_data: dict) -> bool:
        """Post transaction to API service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f'{self.api_base_url}/transactions', json=transaction_data
                )
                response.raise_for_status()
                print(f'Successfully posted transaction to API: {response.status_code}')
                return True
        except Exception as e:
            print(f'Failed to post transaction to API: {e}')
            return False

    async def health_check(self) -> dict:
        """Check API connectivity"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f'{self.api_base_url}/health/')
                response.raise_for_status()
                return {
                    'api_status': 'healthy',
                    'api_reachable': True,
                    'response_code': response.status_code,
                }
        except Exception as e:
            return {'api_status': 'unhealthy', 'api_reachable': False, 'error': str(e)}


# Global API client
api_client = APIClient()


def transform_transaction(incoming_transaction: IncomingTransaction) -> Transaction:
    """Transform incoming transaction to internal format"""
    amount = float(incoming_transaction.Amount.replace('$', ''))
    is_fraud = incoming_transaction.is_fraud == 'Yes'

    # split time string into hours and minutes
    time_parts = incoming_transaction.Time.split(':')
    hour, minute = int(time_parts[0]), int(time_parts[1])

    return Transaction(
        user=incoming_transaction.User,
        card=incoming_transaction.Card,
        year=incoming_transaction.Year,
        month=incoming_transaction.Month,
        day=incoming_transaction.Day,
        time=datetime.time(hour, minute),
        amount=amount,
        use_chip=incoming_transaction.use_chip,
        merchant_id=incoming_transaction.merchant_name,
        merchant_city=incoming_transaction.merchant_city,
        merchant_state=incoming_transaction.merchant_state,
        zip=incoming_transaction.zip,
        mcc=incoming_transaction.mcc,
        errors=incoming_transaction.errors,
        is_fraud=is_fraud,
    )


def transform_to_api_format(transaction: Transaction) -> dict:
    """Transform transaction to API TransactionCreate format"""
    # Create transaction date from year, month, day, time
    transaction_date = datetime.datetime.combine(
        datetime.date(transaction.year, transaction.month, transaction.day),
        transaction.time,
    )

    return {
        'id': str(uuid.uuid4()),
        'user_id': str(transaction.user),
        'credit_card_num': str(transaction.card),
        'amount': transaction.amount,
        'currency': 'USD',
        'description': f'Transaction at {transaction.merchant_id}',
        'merchant_name': str(transaction.merchant_id),
        'merchant_category': str(transaction.mcc),
        'transaction_date': transaction_date.isoformat(),
        'transaction_type': 'PURCHASE',
        'merchant_city': transaction.merchant_city,
        'merchant_state': transaction.merchant_state,
        'merchant_country': 'US',
        'merchant_zipcode': transaction.zip,
        'status': 'PENDING',
        'trans_num': None,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    print('Ingestion service starting up...')
    yield
    print('Ingestion service shutting down...')


app = FastAPI(lifespan=lifespan)


@app.post('/transactions/')
async def create_transaction(incoming_transaction: IncomingTransaction):
    """Create and process a transaction"""
    transaction = transform_transaction(incoming_transaction)
    print(f'Received transaction: {transaction.model_dump()}')

    # Transform to API format and post to API service
    api_transaction_data = transform_to_api_format(transaction)
    api_success = await api_client.post_transaction(api_transaction_data)

    if not api_success:
        print('Warning: Transaction processed but not sent to API service')
        # Still return the transaction even if API posting fails

    return transaction


@app.get('/healthz')
async def healthz():
    """Simple health check endpoint"""
    return {'status': 'ok'}


@app.get('/health')
async def health():
    """Health check endpoint including API connectivity"""
    api_health = await api_client.health_check()
    overall_status = 'healthy' if api_health['api_status'] == 'healthy' else 'degraded'

    return {
        'status': overall_status,
        'service': 'ingestion-service',
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
        'api': api_health,
        'environment': {
            'api_host': api_client.api_host,
            'api_port': api_client.api_port,
            'api_base_url': api_client.api_base_url,
        },
    }
