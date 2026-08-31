import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.database.session import get_engine
from src.core.redis_client import close_redis
from src.core.redis_client import init_redis as connect_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init_postgres(db_engine: AsyncEngine) -> None:
    try:
        async with AsyncSession(db_engine) as session:
            await session.execute(select(1))
    except Exception as e:
        logger.error(e)
        raise e


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init_redis() -> None:
    client = None
    try:
        client = await connect_redis()
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        if client is not None:
            await close_redis(client)


async def main() -> None:
    logger.info("Initializing services")
    engine = get_engine()
    await init_postgres(engine)
    await init_redis()
    logger.info("Services finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
