from uuid import UUID

from src.modules.friends.domain.entities.schemas import FriendRequestWithUser
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)
from src.shared.errors import LumiereError
from src.shared.result import Result


class GetFriendsQuery:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def __call__(
        self, user_id: UUID
    ) -> Result[list[FriendRequestWithUser], LumiereError]:
        friends = await self._friends.get_friends(user_id)
        return Result.ok(friends)
