from typing import Protocol
from uuid import UUID

from src.modules.users.application.commands.create_user import CreateUserCommand
from src.modules.users.application.queries.get_user_by_id import GetUserByIDQuery
from src.modules.users.application.queries.get_user_by_username import (
    GetUserByUsernameQuery,
)
from src.modules.users.application.queries.verify_credentials import (
    VerifyCredentialsQuery,
)
from src.modules.users.domain.entities.dtos import UserDTO, user_to_dto
from src.modules.users.domain.entities.user import User
from src.shared.application.mediator import Mediator
from src.shared.errors import LumiereError
from src.shared.result import Result


class UsersFacade(Protocol):
    """The only way other modules may reach `users`. Exposes DTOs/Results,
    never the User entity or password_hash."""

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
    ) -> Result[UserDTO, LumiereError]: ...

    async def verify_credentials(
        self,
        *,
        username: str,
        plain_password: str,
    ) -> Result[UserDTO, LumiereError]: ...


class MediatorUsersFacade:
    def __init__(self, mediator: Mediator) -> None:
        self._mediator = mediator

    async def get_user(self, user_id: UUID) -> UserDTO | None:
        result: Result[UserDTO, LumiereError] = await self._mediator.query(
            GetUserByIDQuery(user_id=user_id)
        )
        if result.is_err:
            return None
        return result.value

    async def get_user_by_username(self, username: str) -> UserDTO | None:
        result: Result[User, LumiereError] = await self._mediator.query(
            GetUserByUsernameQuery(username=username)
        )
        if result.is_err:
            return None
        return user_to_dto(result.value)

    async def user_exists(self, user_id: UUID) -> bool:
        return await self.get_user(user_id) is not None

    async def create_user(
        self,
        *,
        name: str,
        username: str,
        email: str,
        plain_password: str,
    ) -> Result[UserDTO, LumiereError]:
        result: Result[User, LumiereError] = await self._mediator.send(
            CreateUserCommand(
                name=name,
                username=username,
                email=email,
                plain_password=plain_password,
            )
        )
        if result.is_err:
            return Result.err(result.error)
        return Result.ok(user_to_dto(result.value))

    async def verify_credentials(
        self,
        *,
        username: str,
        plain_password: str,
    ) -> Result[UserDTO, LumiereError]:
        result: Result[User, LumiereError] = await self._mediator.query(
            VerifyCredentialsQuery(username=username, plain_password=plain_password)
        )
        if result.is_err:
            return Result.err(result.error)
        return Result.ok(user_to_dto(result.value))
