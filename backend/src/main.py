from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.errors import register_exception_handlers
from src.api.v1.router import build_api_v1_router
from src.composition.container import build_container
from src.core.cache import RedisCache
from src.core.config import settings
from src.core.database.session import get_session_factory
from src.core.event_bus import InMemoryEventBus, RedisStreamsEventBus
from src.core.jobs import CeleryJobDispatcher, celery_app
from src.core.logging import configure_logging, get_logger
from src.core.realtime.notifier import RedisRealtimeNotifier
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.redis import close_redis, init_redis
from src.core.websocket.manager import ConnectionManager
from src.modules.friends.public.facade import build_friends_facade
from src.modules.presence.application.presence_service import PresenceService
from src.modules.presence.application.presence_sweeper import PresenceSweeper
from src.modules.presence.infrastructure.persistence.redis_presence_repository import (
    RedisPresenceRepository,
)
from src.modules.servers.public.facade import build_servers_facade
from src.utils import custom_generate_unique_id

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
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
    # Dispatches background jobs to Celery workers via the shared Redis
    # broker (see core.jobs). Command handlers depend on the JobDispatcher
    # Protocol only, never this concrete adapter or `celery_app` itself.
    app.state.job_dispatcher = CeleryJobDispatcher(celery_app)
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

    # Presence: built once here, not per-request — see PresenceService's
    # own docstring for why connect/disconnect/heartbeat bypass the
    # mediator entirely. `lookup_presence_fan_out_targets` gives it its own
    # short-lived session for the friend/server lookups a transition needs,
    # sharing the same process-wide pool as ordinary HTTP traffic
    # (deliberate: this only runs on actual transitions, not every
    # heartbeat, so it's infrequent enough not to warrant a dedicated
    # NullPool factory).
    async def lookup_presence_fan_out_targets(
        user_id: UUID,
    ) -> tuple[set[UUID], set[UUID]]:
        async with get_session_factory()() as session:
            friend_ids = await build_friends_facade(session).list_friend_ids(user_id)
            server_ids = await build_servers_facade(session).list_member_server_ids(
                user_id
            )
            return friend_ids, server_ids

    presence_repository = RedisPresenceRepository(
        app.state.redis, stale_after_seconds=settings.WS_PRESENCE_STALE_AFTER_SECONDS
    )
    presence_service = PresenceService(
        presence_repository,
        RedisRealtimeNotifier(redis_subscription_manager),
        lookup_presence_fan_out_targets,
    )
    connection_manager.set_activity_callback(presence_service.on_activity)
    presence_sweeper = PresenceSweeper(
        presence_service,
        interval_seconds=settings.WS_PRESENCE_SWEEP_INTERVAL_SECONDS,
    )
    presence_sweeper.start()
    app.state.presence_service = presence_service
    app.state.presence_sweeper = presence_sweeper

    yield

    logger.info("app.shutdown")
    await app.state.presence_sweeper.stop()
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
