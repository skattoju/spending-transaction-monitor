"""
Database configuration
"""

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""

    # Database settings
    DATABASE_URL: str = (
        'postgresql+asyncpg://user:password@localhost:5432/spending-monitor'
    )

    class Config:
        env_file = '.env'
        extra = 'ignore'


# Global settings instance
settings = DatabaseSettings()
