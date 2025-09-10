"""
Application configuration
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

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

    class Config:
        env_file = '.env'
        extra = 'ignore'  # Allow extra environment variables without validation errors


settings = Settings()
