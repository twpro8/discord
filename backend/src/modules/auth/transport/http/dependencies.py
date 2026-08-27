from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie

from src.api.v1.dependencies import CacheDep, EventBusDep, JobDispatcherDep, SessionDep
from src.modules.auth.adapters.auth_unit_of_work_impl import AuthUnitOfWorkImpl
from src.modules.auth.adapters.persistence.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.modules.auth.domain.exceptions import AuthenticationError
from src.modules.auth.domain.repositories.auth_unit_of_work import AuthUnitOfWork
from src.modules.auth.usecases.login import LoginUseCase
from src.modules.auth.usecases.logout import LogoutUseCase
from src.modules.auth.usecases.refresh import RefreshUseCase
from src.modules.auth.usecases.register import RegisterUseCase
from src.modules.email.public.facade import EmailFacade, build_email_facade
from src.modules.users.public.facade import UsersFacade, build_users_facade

refresh_cookie_scheme = APIKeyCookie(name="refresh_token", auto_error=False)


def get_refresh_token_cookie(token: OptionalRefreshTokenDep) -> str:
    if token is None:
        raise AuthenticationError
    return token


OptionalRefreshTokenDep = Annotated[str | None, Depends(refresh_cookie_scheme)]
RefreshTokenDep = Annotated[str, Depends(get_refresh_token_cookie)]


async def get_auth_unit_of_work(session: SessionDep) -> AsyncGenerator[AuthUnitOfWork]:
    refresh_token_repository = RefreshTokenRepositoryImpl(session)
    async with AuthUnitOfWorkImpl(session, refresh_token_repository) as uow:
        yield uow


def get_users_facade(
    session: SessionDep, cache: CacheDep, event_bus: EventBusDep
) -> UsersFacade:
    return build_users_facade(session, cache, event_bus)


def get_email_facade(
    session: SessionDep, job_dispatcher: JobDispatcherDep
) -> EmailFacade:
    return build_email_facade(session, job_dispatcher)


AuthUnitOfWorkDep = Annotated[AuthUnitOfWork, Depends(get_auth_unit_of_work)]
UsersFacadeDep = Annotated[UsersFacade, Depends(get_users_facade)]
EmailFacadeDep = Annotated[EmailFacade, Depends(get_email_facade)]


async def get_login_use_case(
    uow: AuthUnitOfWorkDep, users_facade: UsersFacadeDep, email_facade: EmailFacadeDep
) -> LoginUseCase:
    return LoginUseCase(uow, users_facade, email_facade)


async def get_register_use_case(users_facade: UsersFacadeDep) -> RegisterUseCase:
    return RegisterUseCase(users_facade)


async def get_refresh_use_case(uow: AuthUnitOfWorkDep) -> RefreshUseCase:
    return RefreshUseCase(uow)


async def get_logout_use_case(uow: AuthUnitOfWorkDep) -> LogoutUseCase:
    return LogoutUseCase(uow)


LoginUseCaseDep = Annotated[LoginUseCase, Depends(get_login_use_case)]
RegisterUseCaseDep = Annotated[RegisterUseCase, Depends(get_register_use_case)]
RefreshUseCaseDep = Annotated[RefreshUseCase, Depends(get_refresh_use_case)]
LogoutUseCaseDep = Annotated[LogoutUseCase, Depends(get_logout_use_case)]
