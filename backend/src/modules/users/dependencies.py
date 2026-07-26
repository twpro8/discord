from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.kernel.dependencies import AccessTokenDep, SessionDep
from src.modules.auth.exceptions import InvalidAccessTokenError
from src.modules.auth.security import decode_access_token
from src.modules.users.repository import UserRepository
from src.modules.users.schemas import User
from src.modules.users.service import UserService
from src.modules.users.unit_of_work import UserUnitOfWork


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


async def get_user_unit_of_work(
    session: SessionDep,
    user_repository: UserRepositoryDep,
) -> AsyncGenerator[UserUnitOfWork]:
    async with UserUnitOfWork(session, user_repository) as user_unit_of_work:
        yield user_unit_of_work


def get_user_service(user_unit_of_work: UserUnitOfWorkDep) -> UserService:
    return UserService(user_unit_of_work)


def get_current_user_id(access_token: AccessTokenDep) -> UUID:
    user_id = decode_access_token(access_token).get("sub")
    if not user_id:
        raise InvalidAccessTokenError
    return UUID(user_id)


async def get_current_user(
    user_id: UserIdDep,
    user_service: UserServiceDep,
) -> User:
    return await user_service.get_user(user_id)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
UserUnitOfWorkDep = Annotated[UserUnitOfWork, Depends(get_user_unit_of_work)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserIdDep = Annotated[UUID, Depends(get_current_user_id)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
