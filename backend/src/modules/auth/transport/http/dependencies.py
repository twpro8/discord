from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie

from src.api.v1.dependencies import SessionDep
from src.modules.auth.application.commands.login import LoginCommand
from src.modules.auth.application.commands.logout import LogoutCommand
from src.modules.auth.application.commands.refresh import RefreshCommand
from src.modules.auth.application.commands.register import RegisterCommand
from src.modules.auth.domain.exceptions import AuthenticationError
from src.modules.auth.infrastructure.auth_unit_of_work_impl import AuthUnitOfWork
from src.modules.auth.infrastructure.persistence.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.modules.users.transport.http.dependencies import UserRepositoryDep

refresh_cookie_scheme = APIKeyCookie(name="refresh_token", auto_error=False)


def get_refresh_token_repository(session: SessionDep) -> RefreshTokenRepositoryImpl:
    return RefreshTokenRepositoryImpl(session)


async def get_auth_unit_of_work(
    session: SessionDep,
    user_repository: UserRepositoryDep,
    refresh_token_repository: RefreshTokenRepositoryDep,
) -> AsyncGenerator[AuthUnitOfWork]:
    async with AuthUnitOfWork(
        session,
        user_repository,
        refresh_token_repository,
    ) as auth_unit_of_work:
        yield auth_unit_of_work


def get_register_command(uow: AuthUnitOfWorkDep) -> RegisterCommand:
    return RegisterCommand(uow)


def get_login_command(uow: AuthUnitOfWorkDep) -> LoginCommand:
    return LoginCommand(uow)


def get_refresh_command(uow: AuthUnitOfWorkDep) -> RefreshCommand:
    return RefreshCommand(uow)


def get_logout_command(uow: AuthUnitOfWorkDep) -> LogoutCommand:
    return LogoutCommand(uow)


def get_refresh_token_cookie(token: OptionalRefreshTokenDep) -> str:
    if token is None:
        raise AuthenticationError
    return token


RefreshTokenRepositoryDep = Annotated[
    RefreshTokenRepositoryImpl, Depends(get_refresh_token_repository)
]
AuthUnitOfWorkDep = Annotated[AuthUnitOfWork, Depends(get_auth_unit_of_work)]
RegisterCommandDep = Annotated[RegisterCommand, Depends(get_register_command)]
LoginCommandDep = Annotated[LoginCommand, Depends(get_login_command)]
RefreshCommandDep = Annotated[RefreshCommand, Depends(get_refresh_command)]
LogoutCommandDep = Annotated[LogoutCommand, Depends(get_logout_command)]
OptionalRefreshTokenDep = Annotated[str | None, Depends(refresh_cookie_scheme)]
RefreshTokenDep = Annotated[str, Depends(get_refresh_token_cookie)]
