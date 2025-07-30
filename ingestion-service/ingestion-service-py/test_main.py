from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

@patch('main.KafkaProducer', new_callable=MagicMock)
def test_create_transaction(mock_kafka_producer):
    with TestClient(app) as client:
        response = client.post(
            "/transactions/",
            json={"user_id": 1, "card_id": 1, "amount": 10.0, "description": "test"},
        )
        assert response.status_code == 200
        assert response.json() == {"user_id": 1, "card_id": 1, "amount": 10.0, "description": "test"}
        mock_kafka_producer.return_value.send.assert_called_once_with('transactions', {'user_id': 1, 'card_id': 1, 'amount': 10.0, 'description': 'test'})

@patch('main.KafkaProducer', new_callable=MagicMock)
def test_healthz(mock_kafka_producer):
    with TestClient(app) as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
