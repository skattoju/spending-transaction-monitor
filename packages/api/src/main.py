"""
FastAPI application entry point
"""

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .routes import health
from .routes import transactions as transactions_routes
from .routes import users as users_routes
from .routes import alerts as alerts_routes
from .routes import kafka as kafka_routes, cleanup_kafka_producer
from .services import start_transaction_consumer, stop_transaction_consumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting up application...")
    try:
        event_loop = asyncio.get_running_loop()
        
        # Start Kafka consumer with the event loop
        start_transaction_consumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            topic=settings.KAFKA_TRANSACTIONS_TOPIC,
            group_id=settings.KAFKA_GROUP_ID,
            event_loop=event_loop
        )
        logger.info("Kafka consumer started successfully")
    except Exception as e:
        logger.error(f"Failed to start Kafka consumer: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        stop_transaction_consumer()
        logger.info("Kafka consumer stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping Kafka consumer: {e}")
    
    try:
        cleanup_kafka_producer()
        logger.info("Kafka producer cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up Kafka producer: {e}")


app = FastAPI(
    title='spending-monitor API',
    description='AI-powered alerts for credit card transactions',
    version='0.0.0',
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(health.router, prefix='/health', tags=['health'])
app.include_router(users_routes.router, prefix='/users', tags=['users'])
app.include_router(
    transactions_routes.router, prefix='/transactions', tags=['transactions']
)
app.include_router(
    alerts_routes.router, prefix='/alerts', tags=['alerts']
)
app.include_router(
    kafka_routes.router, prefix='/kafka', tags=['kafka']
)


@app.get('/')
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {'message': 'Welcome to spending-monitor API'}
