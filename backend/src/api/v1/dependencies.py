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
from src.modules.auth.domain.exceptions import InvalidAccessTokenError

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
