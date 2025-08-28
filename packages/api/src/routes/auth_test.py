"""
Simple authentication test endpoint for validating auth infrastructure
"""

from fastapi import APIRouter, Depends

from ..auth.middleware import get_current_user, require_authentication

router = APIRouter()


@router.get('/public')
async def public_endpoint() -> dict:
    """Public endpoint accessible without authentication"""
    return {
        'message': 'This is a public endpoint - no authentication required',
        'authenticated': False,
        'endpoint': '/auth-test/public'
    }


@router.get('/protected')
async def protected_endpoint(user: dict = Depends(require_authentication)) -> dict:
    """Protected endpoint that requires valid JWT authentication"""
    return {
        'message': f'Hello {user.get("username", "User")}! Authentication successful.',
        'authenticated': True,
        'user_id': user.get('id'),
        'username': user.get('username'),
        'endpoint': '/auth-test/protected'
    }


@router.get('/optional-auth')
async def optional_auth_endpoint(user: dict | None = Depends(get_current_user)) -> dict:
    """Endpoint with optional authentication - different response based on auth status"""
    if user:
        return {
            'message': f'Hello {user.get("username", "User")}! You are authenticated.',
            'authenticated': True,
            'user_id': user.get('id'),
            'username': user.get('username'),
            'endpoint': '/auth-test/optional-auth'
        }
    else:
        return {
            'message': 'Hello anonymous user! Authentication is optional for this endpoint.',
            'authenticated': False,
            'endpoint': '/auth-test/optional-auth'
        }
