from uuid import UUID

from src.modules.friends.domain.entities.schemas import FriendRequestWithUser
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)
from src.shared.errors import LumiereError
from src.shared.result import Result


class GetFriendRequestsQuery:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def __call__(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> Result[list[FriendRequestWithUser], LumiereError]:
        requests = await self._friends.get_for_user(user_id, status)
        return Result.ok(requests)
