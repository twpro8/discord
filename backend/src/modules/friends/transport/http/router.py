from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import UserIdDep
from src.modules.friends.domain.entities.dtos import SendFriendRequestData
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.transport.http.dependencies import (
    AcceptFriendRequestUseCaseDep,
    DeleteFriendRequestUseCaseDep,
    GetFriendRequestsUseCaseDep,
    GetFriendsUseCaseDep,
    GetSentFriendRequestsUseCaseDep,
    RemoveFriendUseCaseDep,
    SendFriendRequestUseCaseDep,
)
from src.modules.friends.transport.http.schemas import (
    FriendRequestResponse,
    FriendRequestWithUserResponse,
    SendFriendRequest,
)

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
    use_case: SendFriendRequestUseCaseDep,
) -> FriendRequestResponse:
    request = await use_case(
        sender_id=current_user_id,
        data=SendFriendRequestData(username=data.username),
    )
    return FriendRequestResponse.model_validate(request)


@router.get(
    "/requests",
    summary="Get friend requests",
    response_model=list[FriendRequestWithUserResponse],
)
async def get_friend_requests(
    current_user_id: UserIdDep,
    use_case: GetFriendRequestsUseCaseDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUserResponse]:
    requests = await use_case(user_id=current_user_id, status=status)
    return [FriendRequestWithUserResponse.model_validate(r) for r in requests]


@router.get(
    "/requests/sent",
    summary="Get sent friend requests",
    response_model=list[FriendRequestWithUserResponse],
)
async def get_user_sent_requests(
    current_user_id: UserIdDep,
    use_case: GetSentFriendRequestsUseCaseDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUserResponse]:
    requests = await use_case(user_id=current_user_id, status=status)
    return [FriendRequestWithUserResponse.model_validate(r) for r in requests]


@router.get(
    "",
    summary="Get friends list",
    response_model=list[FriendRequestWithUserResponse],
)
async def get_friends(
    current_user_id: UserIdDep,
    use_case: GetFriendsUseCaseDep,
) -> list[FriendRequestWithUserResponse]:
    friends = await use_case(user_id=current_user_id)
    return [FriendRequestWithUserResponse.model_validate(r) for r in friends]


@router.patch(
    "/requests/{request_id}/accept",
    summary="Accept a friend request",
    response_model=FriendRequestResponse,
)
async def accept_friend_request(
    current_user_id: UserIdDep,
    request_id: UUID,
    use_case: AcceptFriendRequestUseCaseDep,
) -> FriendRequestResponse:
    request = await use_case(current_user_id=current_user_id, request_id=request_id)
    return FriendRequestResponse.model_validate(request)


@router.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a friend request (cancel or decline)",
)
async def delete_friend_request(
    current_user_id: UserIdDep,
    request_id: UUID,
    use_case: DeleteFriendRequestUseCaseDep,
) -> None:
    await use_case(current_user_id=current_user_id, request_id=request_id)


@router.delete(
    "/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a friend",
)
async def remove_friend(
    current_user_id: UserIdDep,
    relationship_id: UUID,
    use_case: RemoveFriendUseCaseDep,
) -> None:
    await use_case(current_user_id=current_user_id, relationship_id=relationship_id)
