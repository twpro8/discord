from uuid import UUID

from src.modules.friends.public.facade import FriendsFacade
from src.modules.presence.domain.entities.dtos import PresenceDTO
from src.modules.presence.domain.repositories.presence_repository import (
    PresenceRepository,
)


class GetFriendsPresenceUseCase:
    def __init__(
        self,
        presence_repository: PresenceRepository,
        friends_facade: FriendsFacade,
    ) -> None:
        self._presence = presence_repository
        self._friends_facade = friends_facade

    async def __call__(self, *, user_id: UUID) -> list[PresenceDTO]:
        friend_ids = await self._friends_facade.list_friend_ids(user_id)
        statuses = await self._presence.get_statuses(friend_ids)
        return list(statuses.values())
