from uuid import UUID

from src.modules.friends.domain.entities.dtos import FriendRequestUpdate
from src.modules.friends.domain.entities.friend_request import FriendRequest
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)


class AcceptFriendRequestUseCase:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def __call__(
        self, *, current_user_id: UUID, request_id: UUID
    ) -> FriendRequest:
        request = await self._friends.get_by_id(request_id)
        if request is None:
            raise FriendRequestNotFoundError

        if request.target_user_id != current_user_id:
            raise NotParticipantError

        if request.status != FriendStatus.PENDING:
            raise FriendRequestNotPendingError

        return await self._friends.update(
            request_id, FriendRequestUpdate(status=FriendStatus.FRIENDS)
        )
