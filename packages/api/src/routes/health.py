"""
Health check endpoints
"""

from fastapi import APIRouter
from ..schemas.health import HealthResponse
from datetime import datetime, timezone

# Capture API service startup time
API_START_TIME = datetime.now(timezone.utc)
from fastapi import Depends
from typing import Optional
try:
    from db import DatabaseService, get_db_service
except ImportError:
    # DB package not available
    DatabaseService = None
    get_db_service = None

router = APIRouter()


@router.get("/", response_model=list[HealthResponse])
async def health_check(
    db_service: Optional[DatabaseService] = Depends(get_db_service) if get_db_service else None
) -> list[HealthResponse]:
    """Health check endpoint with dependency injection"""
    api_response = HealthResponse(
        name="API",
        status="healthy",
        message="API is running",
        version="0.0.0",
        start_time=API_START_TIME.isoformat()
    )
    
    # Get database health using dependency injection
    responses = [api_response]
    if db_service:
        db_health = await db_service.health_check()
        db_response = HealthResponse(**db_health)
        responses.append(db_response)
    
    return responses
