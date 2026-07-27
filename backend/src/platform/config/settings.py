from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyUrl, BeforeValidator, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.platform.utils import parse_cors


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

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_SECONDS: int = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

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
