from collections.abc import AsyncGenerator
from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends
from fastapi.requests import Request
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.cache import Cache
from src.core.event_bus import EventBus
from src.core.realtime.notifier import RedisRealtimeNotifier
from src.core.realtime.redis_pubsub import PubSubTransport, RedisPubSubTransport
from src.core.security.jwt import decode_access_token
from src.modules.auth.composition import register_auth_handlers
from src.modules.auth.domain.exceptions import InvalidAccessTokenError
from src.modules.messages.composition import register_message_handlers
from src.modules.servers.composition import register_server_handlers
from src.modules.users.public.facade import MediatorUsersFacade
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.in_process_mediator import InProcessMediator
from src.shared.application.mediator import Mediator

access_cookie_scheme = APIKeyCookie(name="access_token")


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


RedisDep = Annotated[Redis, Depends(get_redis)]


def get_event_bus(request: Request) -> EventBus:
    return cast(EventBus, request.app.state.event_bus)


def get_cache(request: Request) -> Cache:
    return cast(Cache, request.app.state.cache)


def get_pubsub(redis: RedisDep) -> PubSubTransport:
    return RedisPubSubTransport(redis)


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    session_factory = cast(
        async_sessionmaker[AsyncSession], request.app.state.session_factory
    )
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
CacheDep = Annotated[Cache, Depends(get_cache)]
AccessTokenDep = Annotated[str, Depends(access_cookie_scheme)]
PubSubDep = Annotated[PubSubTransport, Depends(get_pubsub)]


def get_current_user_id(access_token: AccessTokenDep) -> UUID:
    user_id = decode_access_token(access_token).get("sub")
    if not user_id:
        raise InvalidAccessTokenError
    return UUID(user_id)


UserIdDep = Annotated[UUID, Depends(get_current_user_id)]


async def get_mediator(
    request: Request,
    session: SessionDep,
    event_bus: EventBusDep,
    cache: CacheDep,
    pubsub: PubSubDep,
) -> AsyncGenerator[Mediator]:
    realtime_notifier = RedisRealtimeNotifier(pubsub)
    # Handed to the static HandlerRegistry (app.state.handler_registry,
    # built once at startup) so a lazily-resolved factory can build the one
    # handler a dispatch needs, scoped to this request's own resources —
    # see shared/application/handler_registry.py and in_process_mediator.py.
    services = RequestServices(
        session=session,
        event_bus=event_bus,
        cache=cache,
        realtime_notifier=realtime_notifier,
    )
    registry = cast(HandlerRegistry, request.app.state.handler_registry)
    mediator = InProcessMediator(registry=registry, services=services)
    # Facades only close over `mediator`, not any handler yet registered
    # on it — safe to build before the modules they wrap are registered
    # below, since dispatch never happens before this generator yields.
    users_facade = MediatorUsersFacade(mediator)

    register_auth_handlers(mediator, session, users_facade)
    register_message_handlers(mediator, session, realtime_notifier)
    register_server_handlers(mediator, session)
    # channels, users, friends, and chats are registry-driven (see
    # composition/handlers.py) -- no eager calls needed for them here.
    yield mediator


MediatorDep = Annotated[Mediator, Depends(get_mediator)]
