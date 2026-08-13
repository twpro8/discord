from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack
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
from src.core.jobs import JobDispatcher
from src.core.realtime.membership import DistributedRoomMembershipUpdater
from src.core.realtime.notifier import RedisRealtimeNotifier
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.security.jwt import decode_access_token
from src.core.storage import Storage
from src.modules.auth.composition import register_auth_handlers
from src.modules.auth.domain.exceptions import InvalidAccessTokenError
from src.modules.channels.composition import register_channel_handlers
from src.modules.chats.composition import register_chat_handlers
from src.modules.email.composition import register_email_handlers
from src.modules.email.public.facade import build_email_facade
from src.modules.friends.composition import register_friend_handlers
from src.modules.friends.public.facade import build_friends_facade
from src.modules.messages.composition import register_message_handlers
from src.modules.presence.composition import register_presence_handlers
from src.modules.servers.composition import register_server_handlers
from src.modules.servers.public.facade import build_servers_facade
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


def get_storage(request: Request) -> Storage | None:
    return cast(Storage | None, request.app.state.storage)


def get_redis_subscription_manager(request: Request) -> RedisSubscriptionManager:
    return cast(RedisSubscriptionManager, request.app.state.redis_subscription_manager)


def get_job_dispatcher(request: Request) -> JobDispatcher:
    return cast(JobDispatcher, request.app.state.job_dispatcher)


SessionDep = Annotated[AsyncSession, Depends(get_session)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
CacheDep = Annotated[Cache, Depends(get_cache)]
StorageDep = Annotated[Storage | None, Depends(get_storage)]
AccessTokenDep = Annotated[str, Depends(access_cookie_scheme)]
RedisSubscriptionManagerDep = Annotated[
    RedisSubscriptionManager, Depends(get_redis_subscription_manager)
]
JobDispatcherDep = Annotated[JobDispatcher, Depends(get_job_dispatcher)]


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
    redis: RedisDep,
    redis_subscription_manager: RedisSubscriptionManagerDep,
    job_dispatcher: JobDispatcherDep,
    storage: StorageDep,
) -> AsyncGenerator[Mediator]:
    async with AsyncExitStack() as stack:
        mediator = InProcessMediator()
        # Facades only close over `mediator`, not any handler yet registered
        # on it — safe to build before the modules they wrap are registered
        # below, since dispatch never happens before this generator yields.
        users_facade = MediatorUsersFacade(mediator)
        # Session-backed, unlike users_facade above — friends/servers have
        # no command handlers of their own for presence to dispatch
        # through, so these read straight off the request's session
        # instead (same shape as chats_facade/channels_facade elsewhere).
        friends_facade = build_friends_facade(session)
        servers_facade = build_servers_facade(session)
        # Handler-backed, same shape as channels_facade — email has no
        # command handlers registered anywhere else for another module to
        # dispatch through, so this wraps its own SendEmailCommandHandler
        # directly (see modules/email/public/facade.py).
        email_facade = await build_email_facade(session, stack, job_dispatcher)
        # Redis-backed: reaches every instance's local connections, not
        # just this process's — every connection already auto-joins its
        # own user:{user_id} room on connect (see api/v1/ws.py), and
        # RedisSubscriptionManager is already subscribed wherever this
        # instance has a local subscriber (see main.py's lifespan).
        realtime_notifier = RedisRealtimeNotifier(redis_subscription_manager)
        # Cross-instance too: a user's connection open on a different
        # instance than this request is handled on still needs to learn
        # about a new/revoked chat room (see DistributedRoomMembershipUpdater).
        room_membership_updater = DistributedRoomMembershipUpdater(
            redis_subscription_manager
        )

        await register_auth_handlers(
            mediator, session, stack, users_facade, email_facade
        )
        await register_channel_handlers(mediator, session, stack, servers_facade)
        await register_chat_handlers(
            mediator, session, stack, event_bus, users_facade, room_membership_updater
        )
        await register_email_handlers(mediator, session, stack, job_dispatcher)
        await register_friend_handlers(mediator, session, stack, users_facade)
        await register_message_handlers(
            mediator, session, stack, realtime_notifier, room_membership_updater
        )
        await register_presence_handlers(
            mediator, redis, friends_facade, servers_facade
        )
        await register_server_handlers(
            mediator, session, stack, room_membership_updater
        )
        await register_user_handlers(
            mediator, session, stack, event_bus, cache, storage
        )
        yield mediator


MediatorDep = Annotated[Mediator, Depends(get_mediator)]
