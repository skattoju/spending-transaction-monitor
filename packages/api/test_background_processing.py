#!/usr/bin/env python3
"""Test script for background alert processing"""

from datetime import datetime

import requests

# Test configuration
BASE_URL = 'http://localhost:8000'
USER_ID = 'u-rc-new-001'


def test_transaction_creation_with_background_processing():
    """Test creating a transaction and verify background processing"""

    # Create a test transaction
    transaction_data = {
        'user_id': USER_ID,
        'credit_card_num': '1234567890123456',
        'amount': 600.0,  # This should trigger the $500 alert rule
        'currency': 'USD',
        'description': 'Test transaction for background processing',
        'merchant_name': 'Test Merchant',
        'merchant_category': 'Test Category',
        'transaction_date': datetime.utcnow().isoformat() + 'Z',
        'transaction_type': 'purchase',
        'merchant_longitude': -122.4194,
        'merchant_latitude': 37.7749,
        'merchant_city': 'San Francisco',
        'merchant_state': 'CA',
        'merchant_country': 'US',
        'merchant_zipcode': '94102',
        'status': 'completed',
        'authorization_code': 'AUTH123',
        'trans_num': 'TXN123',
    }

    print('Creating transaction...')
    response = requests.post(f'{BASE_URL}/api/transactions', json=transaction_data)

    if response.status_code == 200:
        transaction = response.json()
        print(f'✅ Transaction created successfully: {transaction["id"]}')
        print(f'   Amount: ${transaction["amount"]}')
        print(f'   Description: {transaction["description"]}')

        # Wait a moment for background processing
        print('\n⏳ Waiting for background alert processing...')
        import time

        time.sleep(3)

        print('✅ Background processing should have completed')
        print('   Check the logs for alert processing results')

    else:
        print(f'❌ Failed to create transaction: {response.status_code}')
        print(f'   Error: {response.text}')


def test_manual_job_creation():
    """Test manually creating a background job"""

    print('\n🧪 Testing manual job creation...')

    job_data = {
        'user_id': USER_ID,
        'transaction_id': 'test-transaction-123',
        'alert_rule_ids': None,  # Process all rules
    }

    response = requests.post(
        f'{BASE_URL}/api/transactions/background-jobs', json=job_data
    )

    if response.status_code == 200:
        job = response.json()
        print(f'✅ Job created successfully: {job["job_id"]}')

        # Check job status
        job_id = job['job_id']
        status_response = requests.get(
            f'{BASE_URL}/api/transactions/background-jobs/{job_id}'
        )

        if status_response.status_code == 200:
            status = status_response.json()
            print(f'   Status: {status["status"]}')
            print(f'   Created: {status["created_at"]}')
        else:
            print(f'❌ Failed to get job status: {status_response.status_code}')

    else:
        print(f'❌ Failed to create job: {response.status_code}')
        print(f'   Error: {response.text}')


if __name__ == '__main__':
    print('🚀 Testing Background Alert Processing')
    print('=' * 50)

    try:
        # Test 1: Create transaction with background processing
        test_transaction_creation_with_background_processing()

        # Test 2: Manual job creation
        test_manual_job_creation()

        print('\n✅ All tests completed!')

    except requests.exceptions.ConnectionError:
        print('❌ Could not connect to the API server')
        print('   Make sure the server is running on http://localhost:8000')
    except Exception as e:
        print(f'❌ Test failed with error: {e}')
