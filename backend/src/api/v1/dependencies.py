from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager
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
from src.core.realtime.notifier import RealtimeNotifier, RedisRealtimeNotifier
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.security.jwt import decode_access_token
from src.core.storage import Storage
from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.auth.composition import register_auth_handlers
from src.modules.auth.domain.exceptions import InvalidAccessTokenError
from src.modules.email.public.facade import build_email_facade
from src.modules.friends.public.facade import build_friends_facade
from src.modules.messages.composition import register_message_handlers
from src.modules.presence.composition import register_presence_handlers
from src.modules.servers.public.facade import build_servers_facade
from src.modules.users.public.facade import build_users_facade
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


def get_realtime_notifier(
    redis_subscription_manager: RedisSubscriptionManagerDep,
) -> RealtimeNotifier:
    """Redis-backed: reaches every instance's local connections, not just
    this process's — every connection already auto-joins its own
    user:{user_id} room on connect (see api/v1/ws.py), and
    RedisSubscriptionManager is already subscribed wherever this instance
    has a local subscriber (see main.py's lifespan)."""
    return RedisRealtimeNotifier(redis_subscription_manager)


RealtimeNotifierDep = Annotated[RealtimeNotifier, Depends(get_realtime_notifier)]


def get_room_membership_updater(
    redis_subscription_manager: RedisSubscriptionManagerDep,
) -> RoomMembershipUpdater:
    """Cross-instance too: a user's connection open on a different
    instance than this request is handled on still needs to learn about a
    new/revoked room (see DistributedRoomMembershipUpdater)."""
    return DistributedRoomMembershipUpdater(redis_subscription_manager)


RoomMembershipUpdaterDep = Annotated[
    RoomMembershipUpdater, Depends(get_room_membership_updater)
]


async def get_mediator(
    session: SessionDep,
    event_bus: EventBusDep,
    cache: CacheDep,
    redis: RedisDep,
    redis_subscription_manager: RedisSubscriptionManagerDep,
    job_dispatcher: JobDispatcherDep,
) -> AsyncGenerator[Mediator]:
    async with AsyncExitStack() as stack:
        mediator = InProcessMediator()
        # Use-case-backed, same shape as email_facade below — users has its
        # own router, but other modules (auth, friends, chats) still reach
        # it only through this facade, never the mediator (see
        # modules/users/public/facade.py).
        users_facade = await stack.enter_async_context(
            asynccontextmanager(build_users_facade)(session, cache, event_bus)
        )
        # Session-backed — friends/servers have no command handlers of
        # their own for presence to dispatch through, so these read
        # straight off the request's session instead (same shape as
        # chats_facade/channels_facade elsewhere).
        friends_facade = build_friends_facade(session)
        servers_facade = build_servers_facade(session)
        # Use-case-backed, same shape as channels_facade — email has no
        # router of its own for another module to dispatch through, so
        # this wraps its own SendEmailUseCase directly (see
        # modules/email/public/facade.py). build_email_facade is an async
        # generator (a plain FastAPI-shaped yield dependency, not yet
        # wired through Depends() here mid-migration), so it's driven
        # manually via asynccontextmanager + the shared exit stack.
        email_facade = await stack.enter_async_context(
            asynccontextmanager(build_email_facade)(session, job_dispatcher)
        )
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
        await register_message_handlers(
            mediator, session, stack, realtime_notifier, room_membership_updater
        )
        await register_presence_handlers(
            mediator, redis, friends_facade, servers_facade
        )
        yield mediator


MediatorDep = Annotated[Mediator, Depends(get_mediator)]
