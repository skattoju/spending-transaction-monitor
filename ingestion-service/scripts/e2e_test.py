import requests
import json
from kafka import KafkaConsumer
import time
import os

def main():
    # Send a request to the ingestion service
    transaction = {
        "user_id": 1,
        "card_id": 1,
        "amount": 10.0,
        "description": "e2e test"
    }
    ingestion_service_host = os.environ.get("INGESTION_SERVICE_HOST", "localhost")
    ingestion_service_port = os.environ.get("INGESTION_SERVICE_PORT", "8000")
    print(f"Sending transaction: {transaction}")
    response = requests.post(f"http://{ingestion_service_host}:{ingestion_service_port}/transactions/", json=transaction)
    response.raise_for_status()
    print("Waiting for message to be processed by Kafka...")
    time.sleep(5)

    # Check if the message is in Kafka
    kafka_host = os.environ.get("KAFKA_HOST", "localhost")
    kafka_port = os.environ.get("KAFKA_PORT", "9092")
    consumer = KafkaConsumer(
        'transactions',
        bootstrap_servers=f"{kafka_host}:{kafka_port}",
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    for message in consumer:
        print(f"Received message: {message.value}")
        if message.value == transaction:
            print("Successfully received message from Kafka")
            return

    raise Exception("Failed to receive message from Kafka")

if __name__ == "__main__":
    main()
