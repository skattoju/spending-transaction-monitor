from fastapi import FastAPI
from kafka import KafkaProducer
import json
import os
from contextlib import asynccontextmanager
import sys

from common.models import Transaction, IncomingTransaction
import datetime


producer = None

def transform_transaction(incoming_transaction: IncomingTransaction) -> Transaction:
    amount = float(incoming_transaction.Amount.replace("$", ""))
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
        is_fraud=is_fraud
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer
    kafka_host = os.environ.get("KAFKA_HOST", "localhost")
    kafka_port = os.environ.get("KAFKA_PORT", "9092")
    producer = KafkaProducer(bootstrap_servers=f"{kafka_host}:{kafka_port}",
                             value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'))
    yield
    producer.close()

app = FastAPI(lifespan=lifespan)


@app.post("/transactions/")
async def create_transaction(incoming_transaction: IncomingTransaction):
    transaction = transform_transaction(incoming_transaction)
    print(f"Received transaction: {transaction.dict()}")
    try:
        future = producer.send('transactions', transaction.dict())
        # Block for 'synchronous' sends
        record_metadata = future.get(timeout=10)
        print(f"Successfully sent message to topic '{record_metadata.topic}' at partition {record_metadata.partition} with offset {record_metadata.offset}")
    except Exception as e:
        print(f"Failed to send message to Kafka: {e}")
        # In a real application, you'd probably want to return an error response here
    return transaction

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
