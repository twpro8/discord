from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.errors import register_exception_handlers
from src.api.v1.router import build_api_v1_router
from src.composition.container import build_container
from src.composition.handlers import build_handler_registry
from src.core.cache import RedisCache
from src.core.config import settings
from src.core.database.session import get_engine, get_session_factory
from src.core.event_bus import InMemoryEventBus, RedisStreamsEventBus
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
    # Read-model cache (cache-aside), shares the pool above
    app.state.cache = RedisCache(app.state.redis)
    # Process-wide event bus for cross-module domain events. In-memory in
    # tests (no Redis dependency for assertions); Redis Streams otherwise
    # so events survive a process restart.
    app.state.event_bus = (
        InMemoryEventBus()
        if settings.ENVIRONMENT == "testing"
        else RedisStreamsEventBus(app.state.redis)
    )
    # Database engine/sessionmaker: built once per process, mirroring the
    # Redis pool above, and disposed of on shutdown.
    app.state.db_engine = get_engine()
    app.state.session_factory = get_session_factory(app.state.db_engine)

    yield

    logger.info("app.shutdown")
    # Close Redis connection
    await close_redis(app.state.redis)
    # Dispose the database engine's connection pool
    await app.state.db_engine.dispose()


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
    # Process-lifetime map of command/query type -> handler factory (see
    # composition/handlers.py and shared/application/handler_registry.py).
    # Unrelated to `container` above, which only holds HTTP routers.
    app.state.handler_registry = build_handler_registry()
    app.include_router(build_api_v1_router(container))

    return app


app = create_app()
