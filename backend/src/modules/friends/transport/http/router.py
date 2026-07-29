from uuid import UUID

from fastapi import APIRouter, status

from src.modules.friends.domain.entities.schemas import (
    FriendRequestResponse,
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
    response_model=FriendRequestResponse,
)
async def send_friend_request(
    current_user_id: UserIdDep,
    data: SendFriendRequest,
    command: SendFriendRequestCommandDep,
) -> FriendRequestResponse:
    result = await command(current_user_id, data)
    if result.is_err:
        raise result.error
    return FriendRequestResponse.model_validate(result.value)


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
    result = await query(current_user_id, status)
    if result.is_err:
        raise result.error
    return result.value


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
    result = await query(current_user_id, status)
    if result.is_err:
        raise result.error
    return result.value


@router.get(
    "",
    summary="Get friends list",
    response_model=list[FriendRequestWithUser],
)
async def get_friends(
    current_user_id: UserIdDep,
    query: GetFriendsQueryDep,
) -> list[FriendRequestWithUser]:
    result = await query(current_user_id)
    if result.is_err:
        raise result.error
    return result.value


@router.patch(
    "/requests/{request_id}/accept",
    summary="Accept a friend request",
    response_model=FriendRequestResponse,
)
async def accept_friend_request(
    current_user_id: UserIdDep,
    request_id: UUID,
    command: AcceptFriendRequestCommandDep,
) -> FriendRequestResponse:
    result = await command(current_user_id, request_id)
    if result.is_err:
        raise result.error
    return FriendRequestResponse.model_validate(result.value)


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
    result = await command(current_user_id, request_id)
    if result.is_err:
        raise result.error


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
    result = await command(current_user_id, relationship_id)
    if result.is_err:
        raise result.error
