from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import CacheDep, SessionDep, StorageDep, TransactionDep
from src.modules.users.adapters.persistence.user_repository_impl import (
    UserRepositoryImpl,
)
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.usecases.change_password import ChangePasswordUseCase
from src.modules.users.usecases.delete_user import DeleteUserUseCase
from src.modules.users.usecases.get_user_by_id import GetUserByIDUseCase
from src.modules.users.usecases.update_avatar import UpdateAvatarUseCase
from src.modules.users.usecases.update_user import UpdateUserUseCase


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepositoryImpl(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


async def get_get_user_by_id_use_case(
    user_repository: UserRepositoryDep, cache: CacheDep
) -> GetUserByIDUseCase:
    return GetUserByIDUseCase(user_repository, cache)


async def get_update_user_use_case(
    tx: TransactionDep, user_repository: UserRepositoryDep, cache: CacheDep
) -> UpdateUserUseCase:
    return UpdateUserUseCase(tx, user_repository, cache)


async def get_delete_user_use_case(
    tx: TransactionDep, user_repository: UserRepositoryDep, cache: CacheDep
) -> DeleteUserUseCase:
    return DeleteUserUseCase(tx, user_repository, cache)


async def get_change_password_use_case(
    tx: TransactionDep, user_repository: UserRepositoryDep, cache: CacheDep
) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(tx, user_repository, cache)


async def get_update_avatar_use_case(
    tx: TransactionDep,
    user_repository: UserRepositoryDep,
    cache: CacheDep,
    storage: StorageDep,
) -> UpdateAvatarUseCase:
    return UpdateAvatarUseCase(tx, user_repository, cache, storage)


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
