from dataclasses import dataclass

from src.core.security.hashing import hash_password
from src.modules.users.domain.entities.schemas import UserCreate
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class CreateUserCommand(Command):
    name: str
    username: str
    email: str
    plain_password: str


class CreateUserCommandHandler:
    def __init__(self, uow: UserUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: CreateUserCommand) -> Result[User, LumiereError]:
        user_data = UserCreate(
            name=command.name,
            username=command.username,
            email=command.email,
            password_hash=hash_password(command.plain_password),
        )
        user = await self._uow.users.create(user_data)
        await self._uow.commit()
        return Result.ok(user)
