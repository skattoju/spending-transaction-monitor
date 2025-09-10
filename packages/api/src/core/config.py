"""
Application configuration
"""

import os
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Environment settings
    ENVIRONMENT: Literal['development', 'production', 'staging', 'test'] = 'development'

    # Authentication settings
    BYPASS_AUTH: bool = False

    # Basic settings
    APP_NAME: str = 'spending-monitor'
    DEBUG: bool = False

    # CORS settings
    ALLOWED_HOSTS: list[str] = ['http://localhost:5173']

    # Database settings
    DATABASE_URL: str = (
        'postgresql+asyncpg://user:password@localhost:5432/spending-monitor'
    )

    # LLM settings
    LLM_PROVIDER: str = 'openai'
    NODE_ENV: str = 'development'
    BASE_URL: str = ''
    API_KEY: str = ''
    MODEL: str = 'gpt-3.5-turbo'

    # Keycloak settings
    KEYCLOAK_URL: str = 'http://localhost:8080'
    KEYCLOAK_REALM: str = 'spending-monitor'
    KEYCLOAK_CLIENT_ID: str = 'spending-monitor'

    class Config:
        env_file = '.env'
        extra = 'ignore'  # Allow extra environment variables without validation errors

    def __post_init__(self):
        """Set derived values based on environment"""
        # Auto-enable auth bypass in development if not explicitly set
        if (
            self.ENVIRONMENT == 'development'
            and not hasattr(self, '_bypass_auth_explicitly_set')
            and 'BYPASS_AUTH' not in os.environ
        ):
            self.BYPASS_AUTH = True

        # Set DEBUG based on environment if not explicitly set
        if not hasattr(self, '_debug_explicitly_set') and 'DEBUG' not in os.environ:
            self.DEBUG = self.ENVIRONMENT == 'development'


settings = Settings()
settings.__post_init__()
