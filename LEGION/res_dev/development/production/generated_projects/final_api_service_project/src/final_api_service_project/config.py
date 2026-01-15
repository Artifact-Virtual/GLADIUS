# Configuration management with environment variables
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application configuration settings"""
    PROJECT_NAME: str = "Final API Service Project"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 30
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    PROMETHEUS_PORT: int = 9090

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()