from uuid import UUID

from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)


class RemoveFriendUseCase:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def __call__(self, *, current_user_id: UUID, relationship_id: UUID) -> None:
        request = await self._friends.get_by_id(relationship_id)
        if request is None:
            raise FriendRequestNotFoundError

        if (
            request.user_id != current_user_id
            and request.target_user_id != current_user_id
        ):
            raise NotParticipantError

        if request.status != FriendStatus.FRIENDS:
            raise FriendRequestNotPendingError

        await self._friends.delete(relationship_id)
