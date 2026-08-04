from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.errors import register_exception_handlers
from src.api.v1.router import build_api_v1_router
from src.composition.container import build_container
from src.core.cache import RedisCache
from src.core.config import settings
from src.core.event_bus import InMemoryEventBus, RedisStreamsEventBus
from src.core.logging import configure_logging, get_logger
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.redis import close_redis, init_redis
from src.core.websocket.manager import ConnectionManager
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
    # Owns all locally-open WebSocket connections for this process (see
    # core.websocket.manager). Cross-instance fan-out is a separate layer:
    # RedisSubscriptionManager subscribes to whatever rooms this instance
    # has local subscribers for, and delivers inbound Redis messages back
    # through the same ConnectionManager — construction order needs the
    # two-phase wiring below since each references the other.
    connection_manager = ConnectionManager(queue_maxsize=settings.WS_SEND_QUEUE_MAXSIZE)
    redis_subscription_manager = RedisSubscriptionManager(
        app.state.redis,
        connection_manager,
        backoff_base_seconds=settings.WS_REDIS_BACKOFF_BASE_SECONDS,
        backoff_max_seconds=settings.WS_REDIS_BACKOFF_MAX_SECONDS,
        backoff_jitter=settings.WS_REDIS_BACKOFF_JITTER,
    )
    connection_manager.set_room_transition_callbacks(
        on_room_activated=redis_subscription_manager.on_room_activated,
        on_room_deactivated=redis_subscription_manager.on_room_deactivated,
    )
    redis_subscription_manager.start()
    app.state.connection_manager = connection_manager
    app.state.redis_subscription_manager = redis_subscription_manager

    yield

    logger.info("app.shutdown")
    await app.state.connection_manager.shutdown()
    await app.state.redis_subscription_manager.stop()
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
