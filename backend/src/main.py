from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.core.redis import init_redis, close_redis
from src.core.router import api_router
from src.utils import custom_generate_unique_id

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # --- Startup ---
    configure_logging()
    logger.info("app.startup", env=settings.APP_ENV)

    # Initialize Redis connection pool
    app.state.redis = await init_redis()

    yield

    # --- Shutdown ---
    logger.info("app.shutdown")

    # Gracefully close Redis connection
    await close_redis(app.state.redis)


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALL_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_V1_STR)
