from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.api.v1.dependencies import AccessTokenDep, SessionDep
from src.core.security.jwt import decode_access_token
from src.modules.auth.domain.exceptions import InvalidAccessTokenError
from src.modules.users.application.commands.delete_user import DeleteUserCommand
from src.modules.users.application.commands.update_user import UpdateUserCommand
from src.modules.users.application.queries.get_user_by_id import (
    GetUserByIDQuery,
)
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.domain.repositories.user_unit_of_work import (
    AbstractUserUnitOfWork,
)
from src.modules.users.infrastructure.persistence.repository import (
    UserRepositoryImpl,
)
from src.modules.users.infrastructure.unit_of_work import UserUnitOfWork


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepositoryImpl(session)


async def get_user_unit_of_work(
    session: SessionDep,
    user_repository: UserRepositoryDep,
) -> AsyncGenerator[AbstractUserUnitOfWork]:
    async with UserUnitOfWork(session, user_repository) as user_unit_of_work:
        yield user_unit_of_work


def get_user_by_id_query(user_repository: UserRepositoryDep) -> GetUserByIDQuery:
    return GetUserByIDQuery(user_repository)


def get_update_user_command(uow: UserUnitOfWorkDep) -> UpdateUserCommand:
    return UpdateUserCommand(uow)


def get_delete_user_command(uow: UserUnitOfWorkDep) -> DeleteUserCommand:
    return DeleteUserCommand(uow)


def get_current_user_id(access_token: AccessTokenDep) -> UUID:
    user_id = decode_access_token(access_token).get("sub")
    if not user_id:
        raise InvalidAccessTokenError
    return UUID(user_id)


async def get_current_user(
    user_id: UserIdDep,
    user_use_case: GetUserByIDQueryDep,
) -> User:
    result = await user_use_case(user_id)
    if result.is_err:
        raise result.error
    return result.value


UserRepositoryDep = Annotated[UserRepositoryImpl, Depends(get_user_repository)]
UserUnitOfWorkDep = Annotated[UserUnitOfWork, Depends(get_user_unit_of_work)]
UserIdDep = Annotated[UUID, Depends(get_current_user_id)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
GetUserByIDQueryDep = Annotated[GetUserByIDQuery, Depends(get_user_by_id_query)]
UpdateUserCommandDep = Annotated[UpdateUserCommand, Depends(get_update_user_command)]
DeleteUserCommandDep = Annotated[DeleteUserCommand, Depends(get_delete_user_command)]
