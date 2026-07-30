from uuid import UUID

from fastapi import APIRouter, status

from src.modules.users.transport.http.dependencies import (
    CurrentUserDep,
    DeleteUserCommandDep,
    GetUserByIDQueryDep,
    UpdateUserCommandDep,
    UserIdDep,
)
from src.modules.users.transport.http.schemas import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    user_id: UserIdDep,
    get_user_use_case: GetUserByIDQueryDep,
) -> UserResponse:
    user = await get_user_use_case(user_id=user_id)
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    summary="Get user by id",
    response_model=UserResponse,
)
async def get_user_by_id(
    _: UserIdDep,
    user_id: UUID,
    get_user_use_case: GetUserByIDQueryDep,
) -> UserResponse:
    user = await get_user_use_case(user_id=user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/me",
    summary="Update current user",
    response_model=UserResponse,
)
async def update_user(
    user_id: UserIdDep,
    data: UserUpdateRequest,
    update_user_command: UpdateUserCommandDep,
) -> UserResponse:
    user = await update_user_command(user_id, data)
    return UserResponse.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: CurrentUserDep,
    delete_user_command: DeleteUserCommandDep,
) -> None:
    await delete_user_command(user)
