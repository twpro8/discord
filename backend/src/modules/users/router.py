from uuid import UUID

from fastapi import APIRouter, status

from src.modules.users.dependencies import CurrentUserDep, UserIdDep, UserServiceDep
from src.modules.users.schemas import UserRead, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get current user",
    response_model=UserRead,
)
async def get_current_user(user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(user)


@router.get(
    "/{user_id}",
    summary="Get user by id",
    response_model=UserRead,
)
async def get_user_by_id(
    _: UserIdDep,
    user_id: UUID,
    service: UserServiceDep,
) -> UserRead:
    user = await service.get_user(user_id)
    return UserRead.model_validate(user)


@router.patch(
    "/me",
    summary="Update current user",
    response_model=UserRead,
)
async def update_user(
    user_id: UserIdDep,
    data: UserUpdateRequest,
    service: UserServiceDep,
) -> UserRead:
    user = await service.update(user_id, data)
    return UserRead.model_validate(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: CurrentUserDep, service: UserServiceDep) -> None:
    await service.delete(user)
