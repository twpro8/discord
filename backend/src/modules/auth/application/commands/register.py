from dataclasses import dataclass

from src.modules.auth.domain.entities.dtos import RegisterData
from src.modules.users.domain.entities.dtos import UserDTO
from src.modules.users.public.facade import UsersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class RegisterCommand(Command):
    data: RegisterData


class RegisterCommandHandler:
    def __init__(self, users_facade: UsersFacade) -> None:
        self._users_facade = users_facade

    async def handle(self, command: RegisterCommand) -> Result[UserDTO, LumiereError]:
        data = command.data
        return await self._users_facade.create_user(
            name=data.name,
            username=data.username,
            email=data.email,
            plain_password=data.password,
        )
