from uuid import UUID

from src.modules.friends.domain.entities.dtos import FriendRequestUpdate
from src.modules.friends.domain.entities.friend_request import FriendRequest
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)


class AcceptFriendRequestUseCase:
    def __init__(self, uow: FriendUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self, *, current_user_id: UUID, request_id: UUID
    ) -> FriendRequest:
        request = await self._uow.friends.get_by_id(request_id)
        if request is None:
            raise FriendRequestNotFoundError

        if request.target_user_id != current_user_id:
            raise NotParticipantError

        if request.status != FriendStatus.PENDING:
            raise FriendRequestNotPendingError

        updated = await self._uow.friends.update(
            request_id, FriendRequestUpdate(status=FriendStatus.FRIENDS)
        )
        await self._uow.commit()
        return updated
