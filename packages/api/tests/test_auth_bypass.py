"""
Tests for authentication bypass functionality
"""

import pytest
import os
from unittest.mock import patch
from src.core.config import Settings
from src.auth.middleware import require_authentication, get_current_user


class TestAuthBypass:
    """Test authentication bypass functionality"""
    
    @pytest.mark.asyncio
    async def test_require_authentication_with_bypass_enabled(self):
        """Test that require_authentication returns dev user when bypass is enabled"""
        # Mock settings with bypass enabled
        with patch('src.auth.middleware.settings') as mock_settings:
            mock_settings.BYPASS_AUTH = True
            
            user = await require_authentication(credentials=None)
            
            assert user is not None
            assert user['id'] == 'dev-user-123'
            assert user['email'] == 'developer@example.com'
            assert user['username'] == 'developer'
            assert user['roles'] == ['user', 'admin']
            assert user['is_dev_mode'] is True
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_bypass_enabled(self):
        """Test that get_current_user returns dev user when bypass is enabled"""
        with patch('src.auth.middleware.settings') as mock_settings:
            mock_settings.BYPASS_AUTH = True
            
            user = await get_current_user(credentials=None)
            
            assert user is not None
            assert user['id'] == 'dev-user-123'
            assert user['is_dev_mode'] is True
    
    @pytest.mark.asyncio
    async def test_get_current_user_without_bypass(self):
        """Test that get_current_user returns None when bypass is disabled and no credentials"""
        with patch('src.auth.middleware.settings') as mock_settings:
            mock_settings.BYPASS_AUTH = False
            
            user = await get_current_user(credentials=None)
            
            assert user is None
    
    def test_config_auto_enables_bypass_in_development(self):
        """Test that BYPASS_AUTH is auto-enabled in development mode"""
        # Test with development environment and no explicit BYPASS_AUTH
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}, clear=True):
            settings = Settings()
            settings.__post_init__()
            
            assert settings.ENVIRONMENT == 'development'
            assert settings.BYPASS_AUTH is True
    
    def test_config_respects_explicit_bypass_setting(self):
        """Test that explicit BYPASS_AUTH setting is respected"""
        # Test with development environment but explicit BYPASS_AUTH=false
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'development',
            'BYPASS_AUTH': 'false'
        }, clear=True):
            settings = Settings()
            settings.__post_init__()
            
            assert settings.ENVIRONMENT == 'development'
            assert settings.BYPASS_AUTH is False
    
    def test_config_production_mode_no_auto_bypass(self):
        """Test that production mode doesn't auto-enable bypass"""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}, clear=True):
            settings = Settings()
            settings.__post_init__()
            
            assert settings.ENVIRONMENT == 'production'
            assert settings.BYPASS_AUTH is False
