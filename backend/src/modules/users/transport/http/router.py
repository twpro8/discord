from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import MediatorDep, UserIdDep
from src.modules.users.application.commands.delete_user import DeleteUserCommand
from src.modules.users.application.commands.update_user import UpdateUserCommand
from src.modules.users.application.queries.get_user_by_id import GetUserByIDQuery
from src.modules.users.transport.http.schemas import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    user_id: UserIdDep,
    mediator: MediatorDep,
) -> UserResponse:
    result = await mediator.query(GetUserByIDQuery(user_id=user_id))
    if result.is_err:
        raise result.error
    return UserResponse.model_validate(result.value)


@router.get(
    "/{user_id}",
    summary="Get user by id",
    response_model=UserResponse,
)
async def get_user_by_id(
    _: UserIdDep,
    user_id: UUID,
    mediator: MediatorDep,
) -> UserResponse:
    result = await mediator.query(GetUserByIDQuery(user_id=user_id))
    if result.is_err:
        raise result.error
    return UserResponse.model_validate(result.value)


@router.patch(
    "/me",
    summary="Update current user",
    response_model=UserResponse,
)
async def update_user(
    user_id: UserIdDep,
    data: UserUpdateRequest,
    mediator: MediatorDep,
) -> UserResponse:
    result = await mediator.send(UpdateUserCommand(user_id=user_id, data=data))
    if result.is_err:
        raise result.error
    return UserResponse.model_validate(result.value)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(DeleteUserCommand(user_id=user_id))
    if result.is_err:
        raise result.error
