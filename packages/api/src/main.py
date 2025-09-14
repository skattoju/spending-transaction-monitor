"""
FastAPI application entry point
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .routes import alerts as alerts_routes
from .routes import health
from .routes import transactions as transactions_routes
from .routes import users as users_routes
from .services.alert_monitor import alert_monitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info('Starting up application...')

    # Start the alert monitoring service in the background
    asyncio.create_task(alert_monitor.start_monitoring())
    logger.info('Alert monitoring service started')

    yield

    # Stop the alert monitoring service
    alert_monitor.stop_monitoring()
    logger.info('Alert monitoring service stopped')
    logger.info('Shutting down application...')


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
app.include_router(alerts_routes.router, prefix='/alerts', tags=['alerts'])


@app.get('/')
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {'message': 'Welcome to spending-monitor API'}
