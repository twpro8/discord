"""Application service for sending friend requests."""

# Python modules
from uuid import UUID

# Project modules
from src.core.services import BaseService
from src.friends.exceptions import (
    CannotSendFriendRequestToSelfError,
    FriendRequestAlreadyExistsError,
)
from src.friends.schemas import FriendRequest, FriendRequestCreate, SendFriendRequest
from src.friends.unit_of_work import FriendUnitOfWork
from src.user.exceptions import UserNotFoundError


class FriendService(BaseService):
    """Coordinate validation and persistence of outgoing friend requests."""

    def __init__(self, unit_of_work: FriendUnitOfWork) -> None:
        self.uow = unit_of_work

    async def send_request(
        self,
        sender_id: UUID,
        data: SendFriendRequest,
    ) -> FriendRequest:
        """Create a pending friend request for the user named in *data*.

        Raises:
            UserNotFoundError: If no active user has the requested username.
            CannotSendFriendRequestToSelfError: If sender and target are identical.
            FriendRequestAlreadyExistsError: If the users already have a relationship.
        """
        target_user = await self.uow.users.get_one(
            username=data.username,
            is_active=True,
        )
        if target_user is None:
            raise UserNotFoundError

        if sender_id == target_user.id:
            raise CannotSendFriendRequestToSelfError

        relationship = await self.uow.friends.get_between_users(
            sender_id,
            target_user.id,
        )
        if relationship is not None:
            raise FriendRequestAlreadyExistsError

        request = await self.uow.friends.create(
            FriendRequestCreate(user_id=sender_id, target_user_id=target_user.id)
        )
        await self.uow.commit()
        return request
