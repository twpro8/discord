from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.errors import register_exception_handlers
from src.api.v1.router import build_api_v1_router
from src.composition.container import build_container
from src.core.config import settings
from src.core.event_bus import InMemoryEventBus
from src.core.logging import configure_logging, get_logger
from src.core.redis import close_redis, init_redis
from src.utils import custom_generate_unique_id

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("app.startup", env=settings.ENVIRONMENT)
    # Initialize Redis connection pool
    app.state.redis = await init_redis()
    # Process-wide event bus for cross-module domain events
    app.state.event_bus = InMemoryEventBus()

    yield

    logger.info("app.shutdown")
    # Close Redis connection
    await close_redis(app.state.redis)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        openapi_url="/api/v1/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALL_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    container = build_container()
    app.state.container = container
    app.include_router(build_api_v1_router(container))

    return app


app = create_app()
