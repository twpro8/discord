from uuid import UUID

from src.modules.friends.domain.entities.dtos import FriendRequestWithUser
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)


class GetSentFriendRequestsUseCase:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def __call__(
        self, *, user_id: UUID, status: FriendStatus = FriendStatus.PENDING
    ) -> list[FriendRequestWithUser]:
        return await self._friends.get_user_sent_requests(user_id, status)
