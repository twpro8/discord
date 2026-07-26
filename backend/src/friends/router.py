"""HTTP endpoints for friend requests."""

# Third-party modules
from fastapi import APIRouter, status

# Project modules
from src.friends.dependencies import FriendServiceDep
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
) -> list[FriendRequestWithUser]:
    """Get the current user's pending friend requests."""
    return await service.get_requests(current_user_id)

@router.get(
    "/requests/sent",
    summary="Get sent friend requests",
    response_model=list[FriendRequestWithUser],
)
async def get_user_sent_requests(
    current_user_id: UserIdDep,
    service: FriendServiceDep,
) -> list[FriendRequestWithUser]:
    """Get the current user's pending friend requests sent to others."""
    return await service.get_user_sent_requests(current_user_id)
