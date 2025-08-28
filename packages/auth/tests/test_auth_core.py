"""
Core tests for JWT authentication middleware
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, JWTError
import sys
from pathlib import Path

# Add API package to path for imports
api_path = Path(__file__).parent.parent.parent / "api" / "src"
sys.path.insert(0, str(api_path))

try:
    from middleware.auth import (
        KeycloakJWTBearer,
        get_current_user,
        require_authentication,
        keycloak_jwt
    )
except ImportError:
    pytest.skip("API middleware not available", allow_module_level=True)


# Test data
MOCK_OIDC_CONFIG = {
    "issuer": "http://localhost:8080/realms/spending-monitor",
    "jwks_uri": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs",
}

MOCK_JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "use": "sig",
            "kid": "test-key-id",
            "n": "test-n-value",
            "e": "AQAB"
        }
    ]
}

VALID_TOKEN_CLAIMS = {
    "sub": "user-123",
    "preferred_username": "testuser",
    "email": "test@example.com",
    "realm_access": {"roles": ["user"]},
    "iss": "http://localhost:8080/realms/spending-monitor",
    "aud": "spending-monitor",
    "exp": 9999999999,  # Far future
    "iat": 1000000000,
    "typ": "Bearer"
}


class TestKeycloakJWTBearer:
    """Test the KeycloakJWTBearer class"""

    def test_init(self):
        """Test KeycloakJWTBearer initialization"""
        bearer = KeycloakJWTBearer()
        assert bearer is not None

    @pytest.mark.asyncio
    @patch('middleware.auth.requests.get')
    async def test_get_oidc_config_success(self, mock_get):
        """Test successful OIDC configuration retrieval"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_OIDC_CONFIG
        mock_get.return_value = mock_response

        bearer = KeycloakJWTBearer()
        config = await bearer.get_oidc_config()
        
        assert config == MOCK_OIDC_CONFIG

    @pytest.mark.asyncio
    @patch('middleware.auth.requests.get')
    async def test_get_oidc_config_failure(self, mock_get):
        """Test OIDC configuration retrieval failure"""
        mock_get.side_effect = Exception("Connection failed")
        
        bearer = KeycloakJWTBearer()
        
        with pytest.raises(HTTPException) as exc_info:
            await bearer.get_oidc_config()
        
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    @patch('middleware.auth.jwt.decode')
    @patch.object(KeycloakJWTBearer, 'get_jwks')
    async def test_validate_token_success(self, mock_get_jwks, mock_jwt_decode):
        """Test successful token validation"""
        mock_get_jwks.return_value = MOCK_JWKS
        mock_jwt_decode.return_value = VALID_TOKEN_CLAIMS

        bearer = KeycloakJWTBearer()
        claims = await bearer.validate_token("valid.jwt.token")
        
        assert claims == VALID_TOKEN_CLAIMS

    @pytest.mark.asyncio
    @patch('middleware.auth.jwt.decode')
    @patch.object(KeycloakJWTBearer, 'get_jwks')
    async def test_validate_token_invalid(self, mock_get_jwks, mock_jwt_decode):
        """Test invalid token validation"""
        mock_get_jwks.return_value = MOCK_JWKS
        mock_jwt_decode.side_effect = JWTError("Invalid token")

        bearer = KeycloakJWTBearer()
        
        with pytest.raises(HTTPException) as exc_info:
            await bearer.validate_token("invalid.jwt.token")
        
        assert exc_info.value.status_code == 401


class TestAuthDependencies:
    """Test authentication dependencies"""

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test get_current_user with no credentials returns None"""
        user = await get_current_user(credentials=None)
        assert user is None

    @pytest.mark.asyncio
    @patch.object(keycloak_jwt, 'validate_token')
    async def test_get_current_user_valid_token(self, mock_validate_token):
        """Test get_current_user with valid token"""
        mock_validate_token.return_value = VALID_TOKEN_CLAIMS
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", 
            credentials="valid.jwt.token"
        )
        
        user = await get_current_user(credentials=credentials)
        
        assert user is not None
        assert user['id'] == 'user-123'
        assert user['username'] == 'testuser'
        assert user['email'] == 'test@example.com'

    @pytest.mark.asyncio
    async def test_require_authentication_no_credentials(self):
        """Test require_authentication with no credentials raises 401"""
        with pytest.raises(HTTPException) as exc_info:
            await require_authentication(credentials=None)
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch.object(keycloak_jwt, 'validate_token')
    async def test_require_authentication_valid_token(self, mock_validate_token):
        """Test require_authentication with valid token"""
        mock_validate_token.return_value = VALID_TOKEN_CLAIMS
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", 
            credentials="valid.jwt.token"
        )
        
        user = await require_authentication(credentials=credentials)
        
        assert user is not None
        assert user['id'] == 'user-123'
        assert user['username'] == 'testuser'


@pytest.fixture(autouse=True)
def reset_caches():
    """Reset global caches before each test"""
    import middleware.auth
    middleware.auth._oidc_config_cache = None
    middleware.auth._jwks_cache = None
    middleware.auth._cache_expiry = None
