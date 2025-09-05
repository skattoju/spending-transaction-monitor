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

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = 'localhost:9092'
    KAFKA_TRANSACTIONS_TOPIC: str = 'transactions'
    KAFKA_GROUP_ID: str = 'transaction-processor'
    KAFKA_AUTO_OFFSET_RESET: str = 'earliest'

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
