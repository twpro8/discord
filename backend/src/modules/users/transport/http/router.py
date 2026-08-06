from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status

from src.api.v1.dependencies import MediatorDep, UserIdDep
from src.modules.users.application.commands.change_password import (
    ChangePasswordCommand,
)
from src.modules.users.application.commands.delete_user import DeleteUserCommand
from src.modules.users.application.commands.update_avatar import (
    UpdateAvatarCommand,
)
from src.modules.users.application.commands.update_user import UpdateUserCommand
from src.modules.users.application.queries.get_user_by_id import GetUserByIDQuery
from src.modules.users.domain.entities.dtos import UserUpdate
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
    update_data = unsettable_from_request(data, UserUpdate)
    result = await mediator.send(UpdateUserCommand(user_id=user_id, data=update_data))
    if result.is_err:
        raise result.error
    return UserResponse.model_validate(result.value)


@router.put(
    "/me/avatar",
    summary="Upload current user's avatar",
    response_model=UserResponse,
)
async def update_avatar(
    user_id: UserIdDep,
    mediator: MediatorDep,
    file: UploadFile = File(...),
) -> UserResponse:
    content = await file.read()
    content_type = file.content_type or ""
    result = await mediator.send(
        UpdateAvatarCommand(
            user_id=user_id,
            content=content,
            content_type=content_type,
        )
    )
    if result.is_err:
        raise result.error
    return UserResponse.model_validate(result.value)


@router.post(
    "/me/password",
    summary="Change current user's password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    user_id: UserIdDep,
    data: ChangePasswordRequest,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        ChangePasswordCommand(
            user_id=user_id,
            current_password=data.current_password,
            new_password=data.new_password,
        )
    )
    if result.is_err:
        raise result.error


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(DeleteUserCommand(user_id=user_id))
    if result.is_err:
        raise result.error
