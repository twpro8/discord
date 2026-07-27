from redis.asyncio import Redis, from_url
from redis.exceptions import AuthenticationError, ConnectionError

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


async def init_redis() -> Redis:
    try:
        client = from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
        )
        await client.ping()  # type: ignore[misc]
        logger.info(
            "redis.connected",
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
        )
        return client
    except AuthenticationError as e:
        logger.error(
            "redis.auth_failed",
            host=settings.REDIS_HOST,
            error=str(e),
        )
        raise
    except ConnectionError as e:
        logger.error(
            "redis.connection_failed",
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            error=str(e),
        )
        raise
    except Exception as e:
        logger.error("redis.unexpected_error", error=str(e))
        raise


async def close_redis(client: Redis) -> None:
    await client.aclose()
    logger.info("redis.disconnected")
