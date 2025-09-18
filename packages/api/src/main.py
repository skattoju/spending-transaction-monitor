"""
FastAPI application entry point
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .routes import alerts as alerts_routes
from .routes import health
from .routes import transactions as transactions_routes
from .routes import users as users_routes
from .services.alert_job_queue import alert_job_queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info('Starting up application...')

    # Start the alert job queue
    await alert_job_queue.start()
    logger.info('Alert monitoring service started')

    yield

    await alert_job_queue.stop()
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
