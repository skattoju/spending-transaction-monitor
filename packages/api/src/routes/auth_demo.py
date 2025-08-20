"""
Authentication demo endpoints for testing OAuth2/OIDC integration
"""

from fastapi import APIRouter, Depends

from ..middleware.auth import get_current_user, require_authentication, require_role

router = APIRouter()


@router.get('/public')
async def public_endpoint() -> dict:
    """Public endpoint accessible without authentication"""
    return {
        'message': 'This is a public endpoint accessible without authentication',
        'authenticated': False,
        'endpoint': '/auth-demo/public'
    }


@router.get('/profile') 
async def profile_endpoint(user: dict | None = Depends(get_current_user)) -> dict:
    """Endpoint that shows different content based on authentication status"""
    if user:
        return {
            'message': f'Hello {user.get("username", "User")}! You are authenticated.',
            'authenticated': True,
            'user': {
                'id': user.get('id'),
                'email': user.get('email'), 
                'username': user.get('username'),
                'roles': user.get('roles', [])
            },
            'endpoint': '/auth-demo/profile'
        }
    else:
        return {
            'message': 'Hello anonymous user! You are not authenticated.',
            'authenticated': False,
            'endpoint': '/auth-demo/profile'
        }


@router.get('/protected')
async def protected_endpoint(user: dict = Depends(require_authentication)) -> dict:
    """Protected endpoint that requires valid JWT authentication"""
    return {
        'message': f'Hello {user.get("username", "User")}! This is a protected endpoint.',
        'authenticated': True,
        'user': {
            'id': user.get('id'),
            'email': user.get('email'),
            'username': user.get('username'),
            'roles': user.get('roles', [])
        },
        'endpoint': '/auth-demo/protected'
    }


@router.get('/user-only')
async def user_only_endpoint(user: dict = Depends(require_role('user'))) -> dict:
    """Endpoint that requires 'user' role or higher"""
    return {
        'message': f'Hello {user.get("username", "User")}! You have the required "user" role.',
        'authenticated': True,
        'required_role': 'user',
        'user': {
            'id': user.get('id'),
            'email': user.get('email'),
            'username': user.get('username'), 
            'roles': user.get('roles', [])
        },
        'endpoint': '/auth-demo/user-only'
    }


@router.get('/admin-only')  
async def admin_only_endpoint(user: dict = Depends(require_role('admin'))) -> dict:
    """Endpoint that requires 'admin' role"""
    return {
        'message': f'Hello {user.get("username", "Admin")}! You have administrative privileges.',
        'authenticated': True,
        'required_role': 'admin',
        'user': {
            'id': user.get('id'),
            'email': user.get('email'),
            'username': user.get('username'),
            'roles': user.get('roles', [])
        },
        'endpoint': '/auth-demo/admin-only'
    }


@router.get('/token-info')
async def token_info_endpoint(user: dict = Depends(require_authentication)) -> dict:
    """Endpoint that shows detailed JWT token information"""
    token_claims = user.get('token_claims', {})
    
    return {
        'message': 'JWT Token Information',
        'authenticated': True,
        'user_summary': {
            'id': user.get('id'),
            'email': user.get('email'),
            'username': user.get('username'),
            'roles': user.get('roles', [])
        },
        'token_details': {
            'issuer': token_claims.get('iss'),
            'subject': token_claims.get('sub'),
            'audience': token_claims.get('aud'),
            'issued_at': token_claims.get('iat'),
            'expires_at': token_claims.get('exp'),
            'client_id': token_claims.get('azp'),
            'session_id': token_claims.get('sid'),
            'realm_access': token_claims.get('realm_access'),
            'resource_access': token_claims.get('resource_access'),
        },
        'full_claims': token_claims,
        'endpoint': '/auth-demo/token-info'
    }
