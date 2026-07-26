"""HTTP endpoints for friend requests."""

# Python modules
from uuid import UUID

# Third-party modules
from fastapi import APIRouter, status

# Project modules
from src.friends.dependencies import FriendServiceDep
from src.friends.enums import FriendStatus
from src.friends.schemas import (
    FriendRequest,
    SendFriendRequest,
    FriendRequestWithUser,
)
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.post(
    "/requests",
    status_code=status.HTTP_201_CREATED,
    summary="Send a friend request",
    response_model=FriendRequest,
)
async def send_friend_request(
    current_user_id: UserIdDep,
    data: SendFriendRequest,
    service: FriendServiceDep,
) -> FriendRequest:
    """Send the current user's pending friend request to a username."""
    return await service.send_request(current_user_id, data)


@router.get(
    "/requests",
    summary="Get friend requests",
    response_model=list[FriendRequestWithUser],
)
async def get_friend_requests(
    current_user_id: UserIdDep,
    service: FriendServiceDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUser]:
    """Get the current user's friend requests by status."""
    return await service.get_requests(current_user_id, status)


@router.get(
    "/requests/sent",
    summary="Get sent friend requests",
    response_model=list[FriendRequestWithUser],
)
async def get_user_sent_requests(
    current_user_id: UserIdDep,
    service: FriendServiceDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUser]:
    """Get the current user's sent friend requests by status."""
    return await service.get_user_sent_requests(current_user_id, status)


@router.get(
    "",
    summary="Get friends list",
    response_model=list[FriendRequestWithUser],
)
async def get_friends(
    current_user_id: UserIdDep,
    service: FriendServiceDep,
) -> list[FriendRequestWithUser]:
    """Get all accepted friends for the current user."""
    return await service.get_friends(current_user_id)


@router.patch(
    "/requests/{request_id}/accept",
    summary="Accept a friend request",
    response_model=FriendRequest,
)
async def accept_friend_request(
    current_user_id: UserIdDep,
    request_id: UUID,
    service: FriendServiceDep,
) -> FriendRequest:
    """Accept a pending friend request as the target user."""
    return await service.accept_request(current_user_id, request_id)


@router.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a friend request (cancel or decline)",
)
async def delete_friend_request(
    current_user_id: UserIdDep,
    request_id: UUID,
    service: FriendServiceDep,
) -> None:
    """Delete a pending friend request. Sender cancels, target declines."""
    await service.delete_request(current_user_id, request_id)


@router.delete(
    "/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a friend",
)
async def remove_friend(
    current_user_id: UserIdDep,
    relationship_id: UUID,
    service: FriendServiceDep,
) -> None:
    """Remove a friend relationship."""
    await service.remove_friend(current_user_id, relationship_id)
