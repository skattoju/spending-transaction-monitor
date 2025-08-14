from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

import datetime

@patch('main.KafkaProducer', new_callable=MagicMock)
def test_create_transaction(mock_kafka_producer):
    with TestClient(app) as client:
        incoming_transaction = {
            "User": 1,
            "Card": 1,
            "Year": 2023,
            "Month": 1,
            "Day": 1,
            "Time": "12:00",
            "Amount": "$10.00",
            "Use Chip": "Swipe Transaction",
            "Merchant Name": 123456789,
            "Merchant City": "New York",
            "Merchant State": "NY",
            "Zip": "10001",
            "MCC": 5411,
            "Errors?": "",
            "Is Fraud?": "No"
        }
        response = client.post(
            "/transactions/",
            json=incoming_transaction,
        )
        assert response.status_code == 200

        expected_response = {
            "user": 1,
            "card": 1,
            "year": 2023,
            "month": 1,
            "day": 1,
            "time": "12:00:00",
            "amount": 10.0,
            "use_chip": "Swipe Transaction",
            "merchant_id": 123456789,
            "merchant_city": "New York",
            "merchant_state": "NY",
            "zip": "10001",
            "mcc": 5411,
            "errors": "",
            "is_fraud": False
        }
        assert response.json() == expected_response

        expected_kafka_payload = expected_response.copy()
        expected_kafka_payload["time"] = datetime.time(12, 0)
        mock_kafka_producer.return_value.send.assert_called_once_with('transactions', expected_kafka_payload)

@patch('main.KafkaProducer', new_callable=MagicMock)
def test_healthz(mock_kafka_producer):
    with TestClient(app) as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
