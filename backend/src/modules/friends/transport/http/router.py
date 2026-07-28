from uuid import UUID

from fastapi import APIRouter, status

from src.modules.friends.domain.entities.schemas import (
    FriendRequest,
    FriendRequestWithUser,
    SendFriendRequest,
)
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.transport.http.dependencies import (
    AcceptFriendRequestCommandDep,
    DeleteFriendRequestCommandDep,
    GetFriendRequestsQueryDep,
    GetFriendsQueryDep,
    GetSentFriendRequestsQueryDep,
    RemoveFriendCommandDep,
    SendFriendRequestCommandDep,
)
from src.modules.users.transport.http.dependencies import UserIdDep

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
    command: SendFriendRequestCommandDep,
) -> FriendRequest:
    return await command(current_user_id, data)


@router.get(
    "/requests",
    summary="Get friend requests",
    response_model=list[FriendRequestWithUser],
)
async def get_friend_requests(
    current_user_id: UserIdDep,
    query: GetFriendRequestsQueryDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUser]:
    return await query(current_user_id, status)


@router.get(
    "/requests/sent",
    summary="Get sent friend requests",
    response_model=list[FriendRequestWithUser],
)
async def get_user_sent_requests(
    current_user_id: UserIdDep,
    query: GetSentFriendRequestsQueryDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUser]:
    return await query(current_user_id, status)


@router.get(
    "",
    summary="Get friends list",
    response_model=list[FriendRequestWithUser],
)
async def get_friends(
    current_user_id: UserIdDep,
    query: GetFriendsQueryDep,
) -> list[FriendRequestWithUser]:
    return await query(current_user_id)


@router.patch(
    "/requests/{request_id}/accept",
    summary="Accept a friend request",
    response_model=FriendRequest,
)
async def accept_friend_request(
    current_user_id: UserIdDep,
    request_id: UUID,
    command: AcceptFriendRequestCommandDep,
) -> FriendRequest:
    return await command(current_user_id, request_id)


@router.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a friend request (cancel or decline)",
)
async def delete_friend_request(
    current_user_id: UserIdDep,
    request_id: UUID,
    command: DeleteFriendRequestCommandDep,
) -> None:
    await command(current_user_id, request_id)


@router.delete(
    "/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a friend",
)
async def remove_friend(
    current_user_id: UserIdDep,
    relationship_id: UUID,
    command: RemoveFriendCommandDep,
) -> None:
    await command(current_user_id, relationship_id)
