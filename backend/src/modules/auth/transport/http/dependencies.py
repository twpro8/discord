from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie

from src.api.v1.dependencies import SessionDep
from src.modules.auth.application.service import AuthService
from src.modules.auth.domain.exceptions import AuthenticationError
from src.modules.auth.infrastructure.persistence.repository import (
    RefreshTokenRepository,
)
from src.modules.auth.infrastructure.unit_of_work import AuthUnitOfWork
from src.modules.users.transport.http.dependencies import UserRepositoryDep

refresh_cookie_scheme = APIKeyCookie(name="refresh_token", auto_error=False)


def get_refresh_token_repository(session: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


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


def get_auth_service(
    session: SessionDep,
    auth_unit_of_work: AuthUnitOfWorkDep,
) -> AuthService:
    return AuthService(session, auth_unit_of_work)


def get_refresh_token_cookie(token: OptionalRefreshTokenDep) -> str:
    if token is None:
        raise AuthenticationError
    return token


RefreshTokenRepositoryDep = Annotated[
    RefreshTokenRepository, Depends(get_refresh_token_repository)
]
AuthUnitOfWorkDep = Annotated[AuthUnitOfWork, Depends(get_auth_unit_of_work)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
OptionalRefreshTokenDep = Annotated[str | None, Depends(refresh_cookie_scheme)]
RefreshTokenDep = Annotated[str, Depends(get_refresh_token_cookie)]
