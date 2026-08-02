from collections.abc import AsyncGenerator
from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends
from fastapi.requests import Request
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import Cache
from src.core.database import get_session
from src.core.event_bus import EventBus
from src.core.realtime.notifier import RedisRealtimeNotifier
from src.core.realtime.redis_pubsub import PubSubTransport, RedisPubSubTransport
from src.core.security.jwt import decode_access_token
from src.modules.auth.composition import register_auth_handlers
from src.modules.auth.domain.exceptions import InvalidAccessTokenError
from src.modules.channels.composition import register_channel_handlers
from src.modules.chats.composition import register_chat_handlers
from src.modules.friends.composition import register_friend_handlers
from src.modules.messages.composition import register_message_handlers
from src.modules.servers.composition import register_server_handlers
from src.modules.users.composition import register_user_handlers
from src.modules.users.public.facade import MediatorUsersFacade
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
    session: SessionDep,
    event_bus: EventBusDep,
    cache: CacheDep,
    pubsub: PubSubDep,
) -> AsyncGenerator[Mediator]:
    mediator = InProcessMediator()
    # Facades only close over `mediator`, not any handler yet registered
    # on it — safe to build before the modules they wrap are registered
    # below, since dispatch never happens before this generator yields.
    users_facade = MediatorUsersFacade(mediator)
    realtime_notifier = RedisRealtimeNotifier(pubsub)

    register_auth_handlers(mediator, session, users_facade)
    register_channel_handlers(mediator, session)
    register_chat_handlers(mediator, session, event_bus, users_facade)
    register_friend_handlers(mediator, session, users_facade)
    register_message_handlers(mediator, session, realtime_notifier)
    register_server_handlers(mediator, session)
    register_user_handlers(mediator, session, event_bus, cache)
    yield mediator


MediatorDep = Annotated[Mediator, Depends(get_mediator)]
