"""Application service for sending friend requests."""

# Python modules
from uuid import UUID

# Project modules
from src.core.services import BaseService
from src.modules.friend.enums import FriendStatus
from src.modules.friend.exceptions import (
    CannotSendFriendRequestToSelfError,
    FriendRequestAlreadyExistsError,
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from src.modules.friend.schemas import (
    FriendRequest,
    FriendRequestCreate,
    FriendRequestUpdate,
    FriendRequestWithUser,
    SendFriendRequest,
)
from src.modules.friend.unit_of_work import FriendUnitOfWork
from src.modules.user.exceptions import UserNotFoundError


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

    async def get_requests(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]:
        """Get friend requests targeted at *user_id* for the given *status*."""
        return await self.uow.friends.get_for_user(user_id, status)

    async def get_user_sent_requests(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]:
        """Get friend requests sent by *user_id* for the given *status*."""
        return await self.uow.friends.get_user_sent_requests(user_id, status)

    async def accept_request(
        self,
        current_user_id: UUID,
        request_id: UUID,
    ) -> FriendRequest:
        """Accept a pending friend request as the target user.

        Raises:
            FriendRequestNotFoundError: If the request does not exist.
            NotParticipantError: If the current user is not the target.
            FriendRequestNotPendingError: If the request is not pending.
        """
        request = await self.uow.friends.get_by_id(request_id)
        if request is None:
            raise FriendRequestNotFoundError

        if request.target_user_id != current_user_id:
            raise NotParticipantError

        if request.status != FriendStatus.PENDING:
            raise FriendRequestNotPendingError

        updated = await self.uow.friends.update(
            request_id,
            FriendRequestUpdate(status=FriendStatus.FRIENDS),
        )
        await self.uow.commit()
        return updated

    async def delete_request(
        self,
        current_user_id: UUID,
        request_id: UUID,
    ) -> None:
        """Delete a pending friend request. Sender cancels, target declines.

        Raises:
            FriendRequestNotFoundError: If the request does not exist.
            NotParticipantError: If the current user is not a participant.
        """
        request = await self.uow.friends.get_by_id(request_id)
        if request is None:
            raise FriendRequestNotFoundError

        if (
            request.user_id != current_user_id
            and request.target_user_id != current_user_id
        ):
            raise NotParticipantError

        await self.uow.friends.delete(request_id)
        await self.uow.commit()

    async def remove_friend(
        self,
        current_user_id: UUID,
        relationship_id: UUID,
    ) -> None:
        """Remove a friend relationship (status=FRIENDS).

        Raises:
            FriendRequestNotFoundError: If the relationship does not exist.
            NotParticipantError: If the current user is not a participant.
            FriendRequestNotPendingError: If the status is not FRIENDS.
        """
        request = await self.uow.friends.get_by_id(relationship_id)
        if request is None:
            raise FriendRequestNotFoundError

        if (
            request.user_id != current_user_id
            and request.target_user_id != current_user_id
        ):
            raise NotParticipantError

        if request.status != FriendStatus.FRIENDS:
            raise FriendRequestNotPendingError

        await self.uow.friends.delete(relationship_id)
        await self.uow.commit()

    async def get_friends(self, user_id: UUID) -> list[FriendRequestWithUser]:
        """Get all accepted friends for the user (both directions)."""
        return await self.uow.friends.get_friends(user_id)
