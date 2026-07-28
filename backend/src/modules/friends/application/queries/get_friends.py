from uuid import UUID

from src.modules.friends.domain.entities.schemas import FriendRequestWithUser
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)


class GetFriendsQuery:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def __call__(self, user_id: UUID) -> list[FriendRequestWithUser]:
        return await self._friends.get_friends(user_id)
