from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os
from contextlib import asynccontextmanager


class Transaction(BaseModel):
    user_id: int
    card_id: int
    amount: float
    description: str

producer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer
    kafka_host = os.environ.get("KAFKA_HOST", "localhost")
    kafka_port = os.environ.get("KAFKA_PORT", "9092")
    producer = KafkaProducer(bootstrap_servers=f"{kafka_host}:{kafka_port}",
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    yield
    producer.close()

app = FastAPI(lifespan=lifespan)


@app.post("/transactions/")
async def create_transaction(transaction: Transaction):
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
