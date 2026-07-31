from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.dtos import ChatUpdate, ChatUpdateData
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class UpdateChatCommand(Command):
    chat_id: UUID
    user_id: UUID
    update_data: ChatUpdateData


class UpdateChatCommandHandler:
    def __init__(self, uow: ChatUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: UpdateChatCommand) -> Result[Chat, LumiereError]:
        try:
            await services.assert_is_group_chat_owner(
                self._uow.chats, self._uow.members, command.user_id, command.chat_id
            )
            updated_chat = await self._uow.chats.update(
                command.chat_id,
                ChatUpdate(
                    name=command.update_data.name,
                    description=command.update_data.description,
                    image_url=command.update_data.image_url,
                ),
            )
        except LumiereError as error:
            return Result.err(error)

        await self._uow.commit()
        return Result.ok(updated_chat)
