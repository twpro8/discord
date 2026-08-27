from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import Cache
from src.core.event_bus import EventBus
from src.modules.users.adapters.persistence.user_repository_impl import (
    UserRepositoryImpl,
)
from src.modules.users.adapters.user_unit_of_work_impl import UserUnitOfWorkImpl
from src.modules.users.domain.entities.dtos import UserDTO, user_to_dto
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.usecases.create_user import CreateUserUseCase
from src.modules.users.usecases.get_user_by_id import GetUserByIDUseCase
from src.modules.users.usecases.get_user_by_username import GetUserByUsernameUseCase
from src.modules.users.usecases.verify_credentials import VerifyCredentialsUseCase


class UsersFacade(Protocol):
    """The only way other modules may reach `users`. Exposes DTOs, never
    the User entity or password_hash."""

    async def get_user(self, user_id: UUID) -> UserDTO | None: ...

    async def get_user_by_username(self, username: str) -> UserDTO | None: ...

    async def user_exists(self, user_id: UUID) -> bool: ...

    async def create_user(
        self,
        *,
        name: str,
        username: str,
        email: str,
        plain_password: str,
    ) -> UserDTO: ...

    async def verify_credentials(
        self,
        *,
        username: str,
        plain_password: str,
    ) -> UserDTO: ...


class UseCaseBackedUsersFacade:
    """Wraps use cases built against the *same* session as the caller —
    same reasoning as `channels.public.facade.UseCaseBackedChannelsFacade`.
    `get_user`/`get_user_by_username` translate a not-found into `None`
    locally; `create_user`/`verify_credentials` let their errors raise."""

    def __init__(
        self,
        get_user_by_id_use_case: GetUserByIDUseCase,
        get_user_by_username_use_case: GetUserByUsernameUseCase,
        verify_credentials_use_case: VerifyCredentialsUseCase,
        create_user_use_case: CreateUserUseCase,
    ) -> None:
        self._get_user_by_id = get_user_by_id_use_case
        self._get_user_by_username = get_user_by_username_use_case
        self._verify_credentials = verify_credentials_use_case
        self._create_user = create_user_use_case

    async def get_user(self, user_id: UUID) -> UserDTO | None:
        try:
            return await self._get_user_by_id(user_id=user_id)
        except UserNotFoundError:
            return None

    async def get_user_by_username(self, username: str) -> UserDTO | None:
        try:
            user = await self._get_user_by_username(username=username)
        except UserNotFoundError:
            return None
        return user_to_dto(user)

    async def user_exists(self, user_id: UUID) -> bool:
        return await self.get_user(user_id) is not None

    async def create_user(
        self,
        *,
        name: str,
        username: str,
        email: str,
        plain_password: str,
    ) -> UserDTO:
        user = await self._create_user(
            name=name, username=username, email=email, plain_password=plain_password
        )
        return user_to_dto(user)

    async def verify_credentials(
        self,
        *,
        username: str,
        plain_password: str,
    ) -> UserDTO:
        user = await self._verify_credentials(
            username=username, plain_password=plain_password
        )
        return user_to_dto(user)


def build_users_facade(
    session: AsyncSession, cache: Cache, event_bus: EventBus
) -> UsersFacade:
    user_repository = UserRepositoryImpl(session)
    uow = UserUnitOfWorkImpl(session, user_repository)
    return UseCaseBackedUsersFacade(
        GetUserByIDUseCase(uow.users, cache),
        GetUserByUsernameUseCase(uow.users),
        VerifyCredentialsUseCase(uow.users),
        CreateUserUseCase(uow, event_bus),
    )
