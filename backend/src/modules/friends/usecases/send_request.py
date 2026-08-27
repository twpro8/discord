from uuid import UUID

from src.modules.friends.domain.entities.dtos import (
    FriendRequestCreate,
    SendFriendRequestData,
)
from src.modules.friends.domain.entities.friend_request import FriendRequest
from src.modules.friends.domain.exceptions import (
    CannotSendFriendRequestToSelfError,
    FriendRequestAlreadyExistsError,
    TargetUserNotFoundError,
)
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)
from src.modules.users.public.facade import UsersFacade


class SendFriendRequestUseCase:
    def __init__(
        self, friend_repository: FriendRepository, users_facade: UsersFacade
    ) -> None:
        self._friends = friend_repository
        self._users_facade = users_facade

    async def __call__(
        self, *, sender_id: UUID, data: SendFriendRequestData
    ) -> FriendRequest:
        target_user = await self._users_facade.get_user_by_username(data.username)
        if not target_user:
            raise TargetUserNotFoundError

        if sender_id == target_user.id:
            raise CannotSendFriendRequestToSelfError

        relationship = await self._friends.get_between_users(sender_id, target_user.id)
        if relationship is not None:
            raise FriendRequestAlreadyExistsError

        return await self._friends.create(
            FriendRequestCreate(user_id=sender_id, target_user_id=target_user.id)
        )
