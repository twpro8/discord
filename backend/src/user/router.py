from fastapi import APIRouter

from src.user.schemas import UserRead, UserUpdateRequest
from src.user.dependencies import UserIdDep, CurrentUserDep, UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get current user",
    response_model=UserRead,
)
async def get_current_user(user: CurrentUserDep) -> UserRead:
    return UserRead.model_validate(user)


@router.patch(
    "",
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
