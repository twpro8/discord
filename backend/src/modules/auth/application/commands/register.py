from dataclasses import dataclass

from src.modules.auth.domain.entities.schemas import RegisterForm
from src.modules.users.domain.entities.schemas import UserDTO
from src.modules.users.public.facade import UsersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class RegisterCommand(Command):
    form_data: RegisterForm


class RegisterCommandHandler:
    def __init__(self, users_facade: UsersFacade) -> None:
        self._users_facade = users_facade

    async def handle(self, command: RegisterCommand) -> Result[UserDTO, LumiereError]:
        form_data = command.form_data
        return await self._users_facade.create_user(
            name=form_data.name,
            username=form_data.username,
            email=form_data.email,
            plain_password=form_data.password,
        )
