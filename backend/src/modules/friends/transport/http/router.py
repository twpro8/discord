from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import MediatorDep
from src.modules.friends.application.commands.accept_request import (
    AcceptFriendRequestCommand,
)
from src.modules.friends.application.commands.delete_request import (
    DeleteFriendRequestCommand,
)
from src.modules.friends.application.commands.remove_friend import RemoveFriendCommand
from src.modules.friends.application.commands.send_request import (
    SendFriendRequestCommand,
)
from src.modules.friends.application.queries.get_friends import GetFriendsQuery
from src.modules.friends.application.queries.get_requests import (
    GetFriendRequestsQuery,
)
from src.modules.friends.application.queries.get_sent_requests import (
    GetSentFriendRequestsQuery,
)
from src.modules.friends.domain.entities.schemas import (
    FriendRequestResponse,
    FriendRequestWithUser,
    SendFriendRequest,
)
from src.modules.friends.domain.enums import FriendStatus
from src.modules.users.transport.http.dependencies import UserIdDep
from src.shared.errors import LumiereError
from src.shared.result import Result

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
    mediator: MediatorDep,
) -> FriendRequestResponse:
    result = await mediator.send(
        SendFriendRequestCommand(sender_id=current_user_id, data=data)
    )
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
    mediator: MediatorDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUser]:
    result: Result[list[FriendRequestWithUser], LumiereError] = await mediator.query(
        GetFriendRequestsQuery(user_id=current_user_id, status=status)
    )
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
    mediator: MediatorDep,
    status: FriendStatus = FriendStatus.PENDING,
) -> list[FriendRequestWithUser]:
    result: Result[list[FriendRequestWithUser], LumiereError] = await mediator.query(
        GetSentFriendRequestsQuery(user_id=current_user_id, status=status)
    )
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
    mediator: MediatorDep,
) -> list[FriendRequestWithUser]:
    result: Result[list[FriendRequestWithUser], LumiereError] = await mediator.query(
        GetFriendsQuery(user_id=current_user_id)
    )
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
    mediator: MediatorDep,
) -> FriendRequestResponse:
    result = await mediator.send(
        AcceptFriendRequestCommand(
            current_user_id=current_user_id, request_id=request_id
        )
    )
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
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        DeleteFriendRequestCommand(
            current_user_id=current_user_id, request_id=request_id
        )
    )
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
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        RemoveFriendCommand(
            current_user_id=current_user_id, relationship_id=relationship_id
        )
    )
    if result.is_err:
        raise result.error
