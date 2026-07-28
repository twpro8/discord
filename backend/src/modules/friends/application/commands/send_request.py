from uuid import UUID

from src.modules.friends.domain.entities.schemas import (
    FriendRequest,
    FriendRequestCreate,
    SendFriendRequest,
)
from src.modules.friends.domain.exceptions import (
    CannotSendFriendRequestToSelfError,
    FriendRequestAlreadyExistsError,
)
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.modules.users.domain.exceptions import UserNotFoundError


class SendFriendRequestCommand:
    def __init__(self, uow: FriendUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, sender_id: UUID, data: SendFriendRequest) -> FriendRequest:
        target_user = await self._uow.users.get_by_username(username=data.username)
        if not target_user or not target_user.is_active:
            raise UserNotFoundError

        if sender_id == target_user.id:
            raise CannotSendFriendRequestToSelfError

        relationship = await self._uow.friends.get_between_users(
            sender_id, target_user.id
        )
        if relationship is not None:
            raise FriendRequestAlreadyExistsError

        request = await self._uow.friends.create(
            FriendRequestCreate(user_id=sender_id, target_user_id=target_user.id)
        )
        await self._uow.commit()
        return request
