from uuid import UUID

from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)


class RemoveFriendUseCase:
    def __init__(self, uow: FriendUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, *, current_user_id: UUID, relationship_id: UUID) -> None:
        request = await self._uow.friends.get_by_id(relationship_id)
        if request is None:
            raise FriendRequestNotFoundError

        if (
            request.user_id != current_user_id
            and request.target_user_id != current_user_id
        ):
            raise NotParticipantError

        if request.status != FriendStatus.FRIENDS:
            raise FriendRequestNotPendingError

        await self._uow.friends.delete(relationship_id)
        await self._uow.commit()
