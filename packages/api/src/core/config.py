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

    class Config:
        env_file = '.env'


settings = Settings()
