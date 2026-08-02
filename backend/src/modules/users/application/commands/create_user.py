from dataclasses import dataclass

from src.core.event_bus import EventBus
from src.core.security.hashing import hash_password
from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import UserError
from src.modules.users.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
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
    def __init__(self, uow: UserUnitOfWork, event_bus: EventBus) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: CreateUserCommand) -> Result[User, LumiereError]:
        try:
            email = Email(command.email)
            username = Username(command.username)
        except UserError as error:
            return Result.err(error)

        user = User.register(
            name=command.name,
            email=email,
            username=username,
            password_hash=hash_password(command.plain_password),
        )
        await self._uow.users.add(user)
        await self._uow.commit()

        await self._event_bus.publish_many(user.pull_events())
        return Result.ok(user)
