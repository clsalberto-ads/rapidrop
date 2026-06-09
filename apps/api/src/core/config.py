from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# .env está na raiz do monorepo (dois níveis acima deste arquivo)
ENV_FILE = Path(__file__).parent.parent.parent.parent.parent / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "RapiDrop API"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://rapidrop:rapidrop_dev@localhost:5432/rapidrop"
    DATABASE_URL_SYNC: str = "postgresql://rapidrop:rapidrop_dev@localhost:5432/rapidrop"

    REDIS_URL: str = "redis://localhost:6379/0"

    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "rapidrop"
    S3_SECRET_KEY: str = "rapidrop_dev"
    S3_BUCKET: str = "rapidrop-assets"

    JWT_SECRET: str = "change-me-to-a-random-secret"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ASAAS_API_KEY: str = ""
    ASAAS_ENVIRONMENT: str = "sandbox"

    SENTRY_DSN: str = ""

    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"
    OTEL_SERVICE_NAME: str = "rapidrop-api"

    DOMAIN: str = "rapidrop.com.br"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"

    model_config = {"env_file": str(ENV_FILE), "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
