from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyUrl, BeforeValidator, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.utils import parse_cors


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=["../.env"],
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_NAME: str = "FastAPI"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str = "default"
    REDIS_PASSWORD: str
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 2
    REDIS_RETRY_ON_TIMEOUT: bool = True

    CELERY_BROKER_DB: int = 1
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    CELERY_TASK_MAX_RETRIES: int = 3
    CELERY_TASK_DEFAULT_RETRY_DELAY: int = 10

    # Emails — consumed by modules/email only (see its infrastructure/providers)
    EMAIL_PROVIDER: Literal["smtp"] = "smtp"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    EMAILS_FROM_EMAIL: str = "info@example.com"
    EMAILS_FROM_NAME: str = "Lumiere"

    # Cloudflare R2 object storage (S3-compatible API). Empty credentials
    # mean storage is not configured: init_storage() skips startup wiring
    # and the app runs without object storage.
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    # Base URL for public object URLs (R2 public bucket or custom domain),
    # e.g. https://pub-<hash>.r2.dev or https://files.example.com
    R2_PUBLIC_BASE_URL: str = ""
    R2_CONNECT_TIMEOUT: float = 5.0
    R2_READ_TIMEOUT: float = 30.0
    R2_MAX_POOL_CONNECTIONS: int = 50
    R2_MAX_AVATAR_BYTES: int = 5_000_000

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_SECONDS: int = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # Bounded per-connection send queue: a WebSocket write slower than the
    # produce rate fails fast (disconnect) past this depth rather than
    # blocking the event loop or silently dropping messages.
    WS_SEND_QUEUE_MAXSIZE: int = 256

    # Reconnect backoff for the realtime Redis subscription listener:
    # delay = min(BASE * 2**attempt, MAX) * uniform(JITTER, 1.0)
    WS_REDIS_BACKOFF_BASE_SECONDS: float = 0.5
    WS_REDIS_BACKOFF_MAX_SECONDS: float = 30.0
    WS_REDIS_BACKOFF_JITTER: float = 0.5

    # Presence heartbeats: how often clients are expected to send one, how
    # long a connection can go without one before the sweeper considers it
    # dead (a crashed tab that never sent a close frame), and how often the
    # sweeper runs.
    WS_PRESENCE_HEARTBEAT_INTERVAL_SECONDS: float = 25.0
    WS_PRESENCE_STALE_AFTER_SECONDS: float = 75.0
    WS_PRESENCE_SWEEP_INTERVAL_SECONDS: float = 30.0

    FRONTEND_HOST: str
    CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field  # type: ignore
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"

    @computed_field  # type: ignore
    @property
    def CELERY_BROKER_URL(self) -> str:
        return (
            f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.CELERY_BROKER_DB}"
        )

    @computed_field  # type: ignore
    @property
    def R2_ENDPOINT_URL(self) -> str:
        return f"https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

    @computed_field  # type: ignore
    @property
    def r2_configured(self) -> bool:
        return bool(
            self.R2_ACCOUNT_ID and self.R2_ACCESS_KEY_ID and self.R2_BUCKET_NAME
        )

    @computed_field  # type: ignore
    @property
    def secure_cookies(self) -> bool:
        """Enable secure only on production (HTTPS)"""
        return self.ENVIRONMENT == "production"

    @computed_field  # type: ignore
    @property
    def ALL_CORS_ORIGINS(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
