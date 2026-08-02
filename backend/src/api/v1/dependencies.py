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
from src.modules.auth.domain.exceptions import InvalidAccessTokenError
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
    # Handed to the composition root's static HandlerRegistry
    # (app.state.container.handler_registry, built once at startup) so a
    # lazily-resolved factory can build the one handler a dispatch needs,
    # scoped to this request's own resources — see composition/container.py,
    # shared/application/handler_registry.py, and in_process_mediator.py.
    # (Not importing Container's type here to read it off app.state.container
    # — composition/container.py transitively imports every module's router,
    # which imports this file, so that import would be circular.)
    services = RequestServices(
        session=session,
        event_bus=event_bus,
        cache=cache,
        realtime_notifier=realtime_notifier,
    )
    registry = cast(HandlerRegistry, request.app.state.container.handler_registry)
    mediator = InProcessMediator(registry=registry, services=services)
    yield mediator


MediatorDep = Annotated[Mediator, Depends(get_mediator)]
