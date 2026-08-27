from uuid import UUID

from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)


class DeleteFriendRequestUseCase:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def __call__(self, *, current_user_id: UUID, request_id: UUID) -> None:
        request = await self._friends.get_by_id(request_id)
        if request is None:
            raise FriendRequestNotFoundError

        if (
            request.user_id != current_user_id
            and request.target_user_id != current_user_id
        ):
            raise NotParticipantError

        await self._friends.delete(request_id)
