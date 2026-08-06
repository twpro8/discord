import botocore
from aiobotocore.session import AioSession
from botocore.config import Config

from src.core.config import settings
from src.core.logging import get_logger
from src.core.storage.storage import R2Storage

logger = get_logger(__name__)


async def init_storage() -> R2Storage | None:
    """Build the R2 client and verify connectivity. Returns None (skipping
    wiring) when R2 credentials aren't configured, so local development and
    tests run without object storage.
    """
    if not settings.r2_configured:
        logger.warning("storage.not_configured")
        return None
    session = AioSession()
    client = await session.create_client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(
            connect_timeout=settings.R2_CONNECT_TIMEOUT,
            read_timeout=settings.R2_READ_TIMEOUT,
            max_pool_connections=settings.R2_MAX_POOL_CONNECTIONS,
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )
    storage = R2Storage(
        client,
        bucket=settings.R2_BUCKET_NAME,
        public_base_url=settings.R2_PUBLIC_BASE_URL,
    )
    try:
        await client.head_bucket(Bucket=settings.R2_BUCKET_NAME)
    except botocore.exceptions.ClientError:
        logger.error("storage.bucket_unreachable", bucket=settings.R2_BUCKET_NAME)
        await storage.close()
        raise
    logger.info("storage.connected", bucket=settings.R2_BUCKET_NAME)
    return storage


async def close_storage(storage: R2Storage) -> None:
    await storage.close()
    logger.info("storage.disconnected")
