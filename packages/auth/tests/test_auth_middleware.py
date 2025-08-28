"""
Comprehensive tests for JWT authentication middleware
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
import respx 
import responses
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add API package to path for imports
api_path = Path(__file__).parent.parent.parent / "api" / "src"
sys.path.insert(0, str(api_path))

try:
    from auth.middleware import (
        KeycloakJWTBearer,
        get_current_user,
        require_authentication,
        require_role,
        require_any_role,
        keycloak_jwt
    )
except ImportError:
    pytest.skip("API middleware not available", allow_module_level=True)


# Test data - Real OIDC config from Keycloak
MOCK_OIDC_CONFIG = {
    "issuer": "http://localhost:8080/realms/spending-monitor",
    "authorization_endpoint": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/auth",
    "token_endpoint": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/token",
    "introspection_endpoint": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/token/introspect",
    "userinfo_endpoint": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/userinfo",
    "end_session_endpoint": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/logout",
    "frontchannel_logout_session_supported": True,
    "frontchannel_logout_supported": True,
    "jwks_uri": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs",
    "check_session_iframe": "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/login-status-iframe.html",
    "grant_types_supported": [
        "authorization_code",
        "implicit", 
        "refresh_token",
        "password",
        "client_credentials",
        "urn:openid:params:grant-type:ciba",
        "urn:ietf:params:oauth:grant-type:device_code"
    ],
    "acr_values_supported": ["0", "1"],
    "response_types_supported": [
        "code", "none", "id_token", "token", "id_token token",
        "code id_token", "code token", "code id_token token"
    ],
    "subject_types_supported": ["public", "pairwise"],
    "id_token_signing_alg_values_supported": [
        "PS384", "ES384", "RS384", "HS256", "HS512", "ES256",
        "RS256", "HS384", "ES512", "PS256", "PS512", "RS512"
    ],
    "scopes_supported": [
        "openid", "roles", "address", "offline_access", "phone",
        "profile", "microprofile-jwt", "email", "web-origins", "acr"
    ],
    "claims_supported": [
        "aud", "sub", "iss", "auth_time", "name", "given_name",
        "family_name", "preferred_username", "email", "acr"
    ]
}

MOCK_JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "use": "sig",
            "kid": "test-key-id",
            "n": "mock-n-value",
            "e": "AQAB",
            "alg": "RS256"
        }
    ]
}

MOCK_JWT_CLAIMS = {
    "sub": "test-user-id",
    "email": "test@example.com",
    "preferred_username": "testuser",
    "realm_access": {
        "roles": ["user"]
    },
    "aud": "spending-monitor",
    "iss": "http://localhost:8080/realms/spending-monitor",
    "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
    "iat": int(datetime.now().timestamp())
}

MOCK_ADMIN_JWT_CLAIMS = {
    **MOCK_JWT_CLAIMS,
    "realm_access": {
        "roles": ["admin", "user"]
    }
}


class TestKeycloakJWTBearer:
    """Test cases for KeycloakJWTBearer class"""

    @pytest.fixture
    def jwt_bearer(self):
        return KeycloakJWTBearer()

    @pytest.fixture
    def mock_http_responses(self):
        """Set up mock HTTP responses for OIDC and JWKS endpoints"""
        with respx.mock:
            # Mock OIDC configuration endpoint
            respx.get(
                "http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration"
            ).mock(return_value=httpx.Response(200, json=MOCK_OIDC_CONFIG))
            
            # Mock JWKS endpoint
            respx.get(
                "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs"
            ).mock(return_value=httpx.Response(200, json=MOCK_JWKS))
            
            yield

    @pytest.mark.asyncio
    async def test_get_oidc_config_success(self, jwt_bearer):
        """Test successful OIDC configuration fetch"""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration",
                json=MOCK_OIDC_CONFIG,
                status=200
            )
            
            config = await jwt_bearer.get_oidc_config()
            
            assert config == MOCK_OIDC_CONFIG
            assert config["issuer"] == "http://localhost:8080/realms/spending-monitor"
            assert "jwks_uri" in config

    @pytest.mark.asyncio
    async def test_get_oidc_config_caching(self, jwt_bearer, mock_http_responses):
        """Test that OIDC configuration is cached"""
        # First call
        config1 = await jwt_bearer.get_oidc_config()
        
        # Second call should use cache (no additional HTTP request)
        config2 = await jwt_bearer.get_oidc_config()
        
        assert config1 == config2

    @pytest.mark.asyncio
    async def test_get_oidc_config_failure_fallback(self, jwt_bearer):
        """Test OIDC configuration graceful fallback when discovery fails"""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration",
                status=500
            )
            
            # Should not raise exception - should gracefully fall back
            config = await jwt_bearer.get_oidc_config()
            
            # Verify fallback config is returned
            assert config is not None
            assert config["issuer"] == "http://localhost:8080/realms/spending-monitor"
            assert config["jwks_uri"] == "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs"
            assert "authorization_endpoint" in config
            assert "token_endpoint" in config

    @pytest.mark.asyncio
    async def test_get_jwks_success(self, jwt_bearer):
        """Test successful JWKS fetch"""
        with responses.RequestsMock() as rsps:
            # Mock OIDC config
            rsps.add(
                responses.GET,
                "http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration",
                json=MOCK_OIDC_CONFIG,
                status=200
            )
            # Mock JWKS
            rsps.add(
                responses.GET,
                "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs",
                json=MOCK_JWKS,
                status=200
            )
            
            jwks = await jwt_bearer.get_jwks()
            
            assert jwks == MOCK_JWKS
            assert "keys" in jwks
            assert len(jwks["keys"]) == 1

    @pytest.mark.asyncio
    async def test_get_jwks_failure(self, jwt_bearer):
        """Test JWKS fetch failure"""
        with responses.RequestsMock() as rsps:
            # Mock successful OIDC config
            rsps.add(
                responses.GET,
                "http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration",
                json=MOCK_OIDC_CONFIG,
                status=200
            )
            # Mock failed JWKS
            rsps.add(
                responses.GET,
                "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs",
                status=500
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await jwt_bearer.get_jwks()
            
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_validate_token_success(self, jwt_bearer, mock_http_responses):
        """Test successful token validation"""
        # Mock jwt.decode to return our test claims
        with patch('auth.middleware.jwt.decode') as mock_decode:
            mock_decode.return_value = MOCK_JWT_CLAIMS
            
            claims = await jwt_bearer.validate_token("mock.jwt.token")
            
            assert claims == MOCK_JWT_CLAIMS
            assert claims["sub"] == "test-user-id"
            assert claims["email"] == "test@example.com"
            
            # Verify jwt.decode was called with correct parameters
            mock_decode.assert_called_once()
            args, kwargs = mock_decode.call_args
            assert args[0] == "mock.jwt.token"  # token
            assert kwargs["algorithms"] == ["RS256"]

    @pytest.mark.asyncio
    async def test_validate_token_jwt_error(self, jwt_bearer, mock_http_responses):
        """Test token validation with JWT error"""
        with patch('auth.middleware.jwt.decode') as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                await jwt_bearer.validate_token("invalid.jwt.token")
            
            assert exc_info.value.status_code == 401
            assert "Invalid token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_token_expired(self, jwt_bearer, mock_http_responses):
        """Test token validation with expired token"""
        with patch('auth.middleware.jwt.decode') as mock_decode:
            mock_decode.side_effect = JWTError("Token expired")
            
            with pytest.raises(HTTPException) as exc_info:
                await jwt_bearer.validate_token("expired.jwt.token")
            
            assert exc_info.value.status_code == 401


class TestAuthDependencies:
    """Test cases for FastAPI auth dependencies"""

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test get_current_user with no credentials"""
        result = await get_current_user(credentials=None)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test get_current_user with valid token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.jwt.token"
        )
        
        with patch.object(keycloak_jwt, 'validate_token') as mock_validate:
            mock_validate.return_value = MOCK_JWT_CLAIMS
            
            result = await get_current_user(credentials=credentials)
            
            assert result is not None
            assert result["id"] == "test-user-id"
            assert result["email"] == "test@example.com"
            assert result["username"] == "testuser"
            assert result["roles"] == ["user"]
            assert "token_claims" in result

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.jwt.token"
        )
        
        with patch.object(keycloak_jwt, 'validate_token') as mock_validate:
            mock_validate.side_effect = HTTPException(status_code=401, detail="Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=credentials)
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_authentication_no_credentials(self):
        """Test require_authentication with no credentials"""
        with pytest.raises(HTTPException) as exc_info:
            await require_authentication(credentials=None)
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_authentication_valid_token(self):
        """Test require_authentication with valid token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.jwt.token"
        )
        
        with patch('auth.middleware.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "test-user-id",
                "email": "test@example.com",
                "roles": ["user"]
            }
            
            result = await require_authentication(credentials=credentials)
            
            assert result["id"] == "test-user-id"
            assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_require_role_success(self):
        """Test require_role with user having required role"""
        user_data = {
            "id": "test-user-id",
            "roles": ["admin", "user"]
        }
        
        # Create role checker for admin role
        admin_checker = require_role("admin")
        
        with patch('auth.middleware.require_authentication') as mock_auth:
            mock_auth.return_value = user_data
            
            result = await admin_checker(user=user_data)
            
            assert result == user_data

    @pytest.mark.asyncio
    async def test_require_role_failure(self):
        """Test require_role with user missing required role"""
        user_data = {
            "id": "test-user-id",
            "roles": ["user"]  # Missing admin role
        }
        
        # Create role checker for admin role
        admin_checker = require_role("admin")
        
        with pytest.raises(HTTPException) as exc_info:
            await admin_checker(user=user_data)
        
        assert exc_info.value.status_code == 403
        assert "Required role: admin" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_any_role_success(self):
        """Test require_any_role with user having one of required roles"""
        user_data = {
            "id": "test-user-id",
            "roles": ["user"]
        }
        
        # Create role checker for user or admin
        role_checker = require_any_role(["user", "admin"])
        
        with patch('auth.middleware.require_authentication') as mock_auth:
            mock_auth.return_value = user_data
            
            result = await role_checker(user=user_data)
            
            assert result == user_data

    @pytest.mark.asyncio
    async def test_require_any_role_failure(self):
        """Test require_any_role with user missing all required roles"""
        user_data = {
            "id": "test-user-id",
            "roles": ["guest"]  # Not user or admin
        }
        
        # Create role checker for user or admin
        role_checker = require_any_role(["user", "admin"])
        
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(user=user_data)
        
        assert exc_info.value.status_code == 403
        assert "Required roles: ['user', 'admin']" in str(exc_info.value.detail)


class TestIntegration:
    """Integration tests for the auth system"""

    @pytest.mark.asyncio
    async def test_full_auth_flow(self):
        """Test complete authentication flow"""
        # Simulate the full flow from token to user data
        token = "valid.jwt.token"
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with respx.mock:
            # Mock OIDC and JWKS endpoints
            respx.get(
                "http://localhost:8080/realms/spending-monitor/.well-known/openid-configuration"
            ).mock(return_value=httpx.Response(200, json=MOCK_OIDC_CONFIG))
            
            respx.get(
                "http://localhost:8080/realms/spending-monitor/protocol/openid-connect/certs"
            ).mock(return_value=httpx.Response(200, json=MOCK_JWKS))
            
            # Mock JWT validation
            with patch('auth.middleware.jwt.decode') as mock_decode:
                mock_decode.return_value = MOCK_ADMIN_JWT_CLAIMS
                
                # Test the full flow
                user = await get_current_user(credentials=credentials)
                
                assert user is not None
                assert user["id"] == "test-user-id"
                assert user["email"] == "test@example.com"
                assert "admin" in user["roles"]
                assert "user" in user["roles"]
                
                # Test admin access
                admin_checker = require_role("admin")
                admin_result = await admin_checker(user=user)
                assert admin_result == user
                
                # Test user access
                user_checker = require_any_role(["user", "admin"])
                user_result = await user_checker(user=user)
                assert user_result == user


# Pytest configuration
@pytest.fixture(autouse=True)
def reset_caches():
    """Reset global caches before each test"""
    import auth.middleware as auth_module
    auth_module._oidc_config_cache = None
    auth_module._jwks_cache = None
    auth_module._cache_expiry = None
    yield
