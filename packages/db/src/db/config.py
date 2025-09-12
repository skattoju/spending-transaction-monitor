"""
Database configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Database settings
    DATABASE_URL: str = (
        'postgresql+asyncpg://user:password@localhost:5432/spending-monitor'
    )


# Global settings instance
settings = DatabaseSettings()
