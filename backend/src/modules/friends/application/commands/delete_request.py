from uuid import UUID

from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)


class DeleteFriendRequestCommand:
    def __init__(self, uow: FriendUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, current_user_id: UUID, request_id: UUID) -> None:
        request = await self._uow.friends.get_by_id(request_id)
        if request is None:
            raise FriendRequestNotFoundError

        if (
            request.user_id != current_user_id
            and request.target_user_id != current_user_id
        ):
            raise NotParticipantError

        await self._uow.friends.delete(request_id)
        await self._uow.commit()
