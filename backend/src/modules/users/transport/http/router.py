from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status

from src.api.v1.dependencies import UserIdDep
from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.transport.http.dependencies import (
    ChangePasswordUseCaseDep,
    DeleteUserUseCaseDep,
    GetUserByIDUseCaseDep,
    UpdateAvatarUseCaseDep,
    UpdateUserUseCaseDep,
)
from src.modules.users.transport.http.schemas import (
    ChangePasswordRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    user_id: UserIdDep,
    use_case: GetUserByIDUseCaseDep,
) -> UserResponse:
    user = await use_case(user_id=user_id)
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    summary="Get user by id",
    response_model=UserResponse,
)
async def get_user_by_id(
    _: UserIdDep,
    user_id: UUID,
    use_case: GetUserByIDUseCaseDep,
) -> UserResponse:
    user = await use_case(user_id=user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/me",
    summary="Update current user",
    response_model=UserResponse,
)
async def update_user(
    user_id: UserIdDep,
    data: UserUpdateRequest,
    use_case: UpdateUserUseCaseDep,
) -> UserResponse:
    update_data = unsettable_from_request(data, UserUpdate)
    user = await use_case(user_id=user_id, data=update_data)
    return UserResponse.model_validate(user)


@router.put(
    "/me/avatar",
    summary="Upload current user's avatar",
    response_model=UserResponse,
)
async def update_avatar(
    user_id: UserIdDep,
    use_case: UpdateAvatarUseCaseDep,
    file: UploadFile = File(...),
) -> UserResponse:
    content = await file.read()
    content_type = file.content_type or ""
    user = await use_case(user_id=user_id, content=content, content_type=content_type)
    return UserResponse.model_validate(user)


@router.post(
    "/me/password",
    summary="Change current user's password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    user_id: UserIdDep,
    data: ChangePasswordRequest,
    use_case: ChangePasswordUseCaseDep,
) -> None:
    await use_case(
        user_id=user_id,
        current_password=data.current_password,
        new_password=data.new_password,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UserIdDep,
    use_case: DeleteUserUseCaseDep,
) -> None:
    await use_case(user_id=user_id)
