import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


__all__ = [
    "AppConfig",
    "config"
]


class AppConfig(BaseSettings):
    VERSION: str = '1.0.0'
    DOCS_URL: str = '/api/openapi'
    OPENAPI_URL: str = '/api/openapi.json'
    PROJECT_NAME: str = 'URL Shortener Service'
    PROJECT_DESCRIPTION: str = 'API сервис для сокращения ссылок'

    DB_CONNECTION: str = "postgresql+asyncpg://postgres:postgres@db:5432/shortener"
    REDIS_CONNECTION: str = "redis://redis:6379/0"
    JWT_SECRET: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_LIFETIME_MINUTES: int = 360
    INACTIVE_LINK_EXPIRY_DAYS: int = 30

    class Config:
        env_file = ".env"


config = AppConfig()