from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import RedisDep, SessionDep
from src.core.config import settings
from src.modules.friends.public.facade import FriendsFacade, build_friends_facade
from src.modules.presence.adapters.persistence.redis_presence_repository import (
    RedisPresenceRepository,
)
from src.modules.presence.domain.repositories.presence_repository import (
    PresenceRepository,
)
from src.modules.presence.usecases.get_friends_presence import (
    GetFriendsPresenceUseCase,
)
from src.modules.presence.usecases.get_server_presence import GetServerPresenceUseCase
from src.modules.servers.public.facade import ServersFacade, build_servers_facade


def get_presence_repository(redis: RedisDep) -> PresenceRepository:
    return RedisPresenceRepository(
        redis, stale_after_seconds=settings.WS_PRESENCE_STALE_AFTER_SECONDS
    )


async def get_friends_facade(session: SessionDep) -> FriendsFacade:
    return build_friends_facade(session)


async def get_servers_facade(session: SessionDep) -> ServersFacade:
    return build_servers_facade(session)


PresenceRepositoryDep = Annotated[PresenceRepository, Depends(get_presence_repository)]
FriendsFacadeDep = Annotated[FriendsFacade, Depends(get_friends_facade)]
ServersFacadeDep = Annotated[ServersFacade, Depends(get_servers_facade)]


async def get_get_friends_presence_use_case(
    presence_repository: PresenceRepositoryDep, friends_facade: FriendsFacadeDep
) -> GetFriendsPresenceUseCase:
    return GetFriendsPresenceUseCase(presence_repository, friends_facade)


async def get_get_server_presence_use_case(
    presence_repository: PresenceRepositoryDep, servers_facade: ServersFacadeDep
) -> GetServerPresenceUseCase:
    return GetServerPresenceUseCase(presence_repository, servers_facade)


GetFriendsPresenceUseCaseDep = Annotated[
    GetFriendsPresenceUseCase, Depends(get_get_friends_presence_use_case)
]
GetServerPresenceUseCaseDep = Annotated[
    GetServerPresenceUseCase, Depends(get_get_server_presence_use_case)
]
