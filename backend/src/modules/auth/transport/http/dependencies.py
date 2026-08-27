from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie

from src.api.v1.dependencies import (
    CacheDep,
    EventBusDep,
    JobDispatcherDep,
    SessionDep,
    TransactionDep,
)
from src.modules.auth.adapters.persistence.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.modules.auth.domain.exceptions import AuthenticationError
from src.modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
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


def get_refresh_token_repository(session: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepositoryImpl(session)


def get_users_facade(
    session: SessionDep, cache: CacheDep, event_bus: EventBusDep
) -> UsersFacade:
    return build_users_facade(session, cache, event_bus)


def get_email_facade(
    session: SessionDep, job_dispatcher: JobDispatcherDep
) -> EmailFacade:
    return build_email_facade(session, job_dispatcher)


RefreshTokenRepositoryDep = Annotated[
    RefreshTokenRepository, Depends(get_refresh_token_repository)
]
UsersFacadeDep = Annotated[UsersFacade, Depends(get_users_facade)]
EmailFacadeDep = Annotated[EmailFacade, Depends(get_email_facade)]


async def get_login_use_case(
    tx: TransactionDep,
    refresh_token_repository: RefreshTokenRepositoryDep,
    users_facade: UsersFacadeDep,
    email_facade: EmailFacadeDep,
) -> LoginUseCase:
    return LoginUseCase(tx, refresh_token_repository, users_facade, email_facade)


async def get_register_use_case(users_facade: UsersFacadeDep) -> RegisterUseCase:
    return RegisterUseCase(users_facade)


async def get_refresh_use_case(
    tx: TransactionDep, refresh_token_repository: RefreshTokenRepositoryDep
) -> RefreshUseCase:
    return RefreshUseCase(tx, refresh_token_repository)


async def get_logout_use_case(
    tx: TransactionDep, refresh_token_repository: RefreshTokenRepositoryDep
) -> LogoutUseCase:
    return LogoutUseCase(tx, refresh_token_repository)


LoginUseCaseDep = Annotated[LoginUseCase, Depends(get_login_use_case)]
RegisterUseCaseDep = Annotated[RegisterUseCase, Depends(get_register_use_case)]
RefreshUseCaseDep = Annotated[RefreshUseCase, Depends(get_refresh_use_case)]
LogoutUseCaseDep = Annotated[LogoutUseCase, Depends(get_logout_use_case)]
