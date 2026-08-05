from redis.asyncio import Redis

from src.core.config.settings import settings
from src.modules.friends.public.facade import FriendsFacade
from src.modules.presence.application.queries.get_friends_presence import (
    GetFriendsPresenceQuery,
    GetFriendsPresenceQueryHandler,
)
from src.modules.presence.application.queries.get_server_presence import (
    GetServerPresenceQuery,
    GetServerPresenceQueryHandler,
)
from src.modules.presence.infrastructure.persistence.redis_presence_repository import (
    RedisPresenceRepository,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.application.in_process_mediator import InProcessMediator


async def register_presence_handlers(
    mediator: InProcessMediator,
    redis: Redis,
    friends_facade: FriendsFacade,
    servers_facade: ServersFacade,
) -> None:
    """Registers only the read side (the two GET /presence/* queries) — the
    write side (connect/disconnect/heartbeat) is PresenceService, built
    once at app startup in main.py's lifespan, not per-request here. See
    PresenceService's own docstring for why it bypasses the mediator
    entirely rather than being registered alongside these queries."""
    presence_repository = RedisPresenceRepository(
        redis, stale_after_seconds=settings.WS_PRESENCE_STALE_AFTER_SECONDS
    )

    mediator.register_query(
        GetFriendsPresenceQuery,
        GetFriendsPresenceQueryHandler(presence_repository, friends_facade),
    )
    mediator.register_query(
        GetServerPresenceQuery,
        GetServerPresenceQueryHandler(presence_repository, servers_facade),
    )
