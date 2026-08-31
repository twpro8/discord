from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.errors import register_exception_handlers
from src.api.v1.router import build_api_v1_router
from src.core.cache import RedisCache
from src.core.config import settings
from src.core.database.session import get_session_factory
from src.core.jobs import CeleryJobDispatcher, celery_app
from src.core.logging import configure_logging, get_logger
from src.core.realtime.manager import ConnectionManager
from src.core.realtime.notifier import RedisRealtimeNotifier
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.redis_client import close_redis, init_redis
from src.core.storage import close_storage, init_storage
from src.core.version import get_app_version
from src.modules.friends.public.facade import build_friends_facade
from src.modules.presence.adapters.persistence.redis_presence_repository import (
    RedisPresenceRepository,
)
from src.modules.presence.application.presence_service import PresenceService
from src.modules.presence.application.presence_sweeper import PresenceSweeper
from src.modules.servers.public.facade import build_servers_facade
from src.modules.typing.application.typing_service import TypingService
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
    # Object storage (Cloudflare R2). None when R2 isn't configured.
    app.state.storage = await init_storage()
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
    # own docstring for why connect/disconnect/heartbeat bypass per-request
    # DI entirely. `lookup_presence_fan_out_targets` gives it its own
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
        app.state.redis,
        stale_after_seconds=settings.WS_PRESENCE_STALE_AFTER_SECONDS,
    )
    presence_service = PresenceService(
        presence_repository,
        RedisRealtimeNotifier(redis_subscription_manager),
        lookup_presence_fan_out_targets,
    )
    typing_service = TypingService(
        connection_manager.is_connection_in_room,
        RedisRealtimeNotifier(redis_subscription_manager),
    )

    async def dispatch_activity(
        user_id: UUID, connection_id: UUID, raw_text: str
    ) -> None:
        # Each call wrapped independently: ConnectionManager.serve()'s
        # reader loop has no try/except of its own around on_activity — an
        # uncaught exception here would propagate up and disconnect the
        # connection, so one service misbehaving must never sink the
        # other.
        for service in (presence_service, typing_service):
            try:
                await service.on_activity(user_id, connection_id, raw_text)
            except Exception:
                logger.exception(
                    "realtime.activity_dispatch_failed",
                    service=type(service).__name__,
                )

    connection_manager.set_activity_callback(dispatch_activity)
    app.state.typing_service = typing_service
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
    # Close R2 storage client if it was initialized
    if app.state.storage is not None:
        await close_storage(app.state.storage)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=get_app_version(),
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

    # Multiprocess-safe (PROMETHEUS_MULTIPROC_DIR, see backend/scripts/start.sh)
    # since uvicorn runs multiple worker processes in Docker. Excludes
    # /metrics itself and the health check from the request metrics so
    # Prometheus's own scrapes and container healthchecks don't skew them.
    Instrumentator(excluded_handlers=["/metrics", "/api/v1/health"]).instrument(
        app
    ).expose(app, include_in_schema=False, tags=["Meta"])

    app.include_router(build_api_v1_router())

    return app


app = create_app()
