from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import CacheDep, SessionDep, StorageDep
from src.modules.users.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.modules.users.infrastructure.persistence.user_repository_impl import (
    UserRepositoryImpl,
)
from src.modules.users.infrastructure.user_unit_of_work_impl import UserUnitOfWorkImpl
from src.modules.users.usecases.change_password import ChangePasswordUseCase
from src.modules.users.usecases.delete_user import DeleteUserUseCase
from src.modules.users.usecases.get_user_by_id import GetUserByIDUseCase
from src.modules.users.usecases.update_avatar import UpdateAvatarUseCase
from src.modules.users.usecases.update_user import UpdateUserUseCase


async def get_user_unit_of_work(session: SessionDep) -> AsyncGenerator[UserUnitOfWork]:
    user_repository = UserRepositoryImpl(session)
    async with UserUnitOfWorkImpl(session, user_repository) as uow:
        yield uow


UserUnitOfWorkDep = Annotated[UserUnitOfWork, Depends(get_user_unit_of_work)]


async def get_get_user_by_id_use_case(
    uow: UserUnitOfWorkDep, cache: CacheDep
) -> GetUserByIDUseCase:
    return GetUserByIDUseCase(uow.users, cache)


async def get_update_user_use_case(
    uow: UserUnitOfWorkDep, cache: CacheDep
) -> UpdateUserUseCase:
    return UpdateUserUseCase(uow, cache)


async def get_delete_user_use_case(
    uow: UserUnitOfWorkDep, cache: CacheDep
) -> DeleteUserUseCase:
    return DeleteUserUseCase(uow, cache)


async def get_change_password_use_case(
    uow: UserUnitOfWorkDep, cache: CacheDep
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(uow, cache)


async def get_update_avatar_use_case(
    uow: UserUnitOfWorkDep, cache: CacheDep, storage: StorageDep
) -> UpdateAvatarUseCase:
    return UpdateAvatarUseCase(uow, cache, storage)


GetUserByIDUseCaseDep = Annotated[
    GetUserByIDUseCase, Depends(get_get_user_by_id_use_case)
]
UpdateUserUseCaseDep = Annotated[UpdateUserUseCase, Depends(get_update_user_use_case)]
DeleteUserUseCaseDep = Annotated[DeleteUserUseCase, Depends(get_delete_user_use_case)]
ChangePasswordUseCaseDep = Annotated[
    ChangePasswordUseCase, Depends(get_change_password_use_case)
]
UpdateAvatarUseCaseDep = Annotated[
    UpdateAvatarUseCase, Depends(get_update_avatar_use_case)
]
