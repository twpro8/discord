from dataclasses import dataclass
from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.entities.dtos import ChatUpdate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import CannotLeavePrivateChatError
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class LeaveChatCommand(Command):
    chat_id: UUID
    user_id: UUID


class LeaveChatCommandHandler:
    def __init__(self, uow: ChatUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: LeaveChatCommand) -> Result[None, LumiereError]:
        try:
            chat = await services.assert_is_chat_member(
                self._uow.chats, self._uow.members, command.user_id, command.chat_id
            )
            if chat.type == ChatType.private:
                raise CannotLeavePrivateChatError
        except LumiereError as error:
            return Result.err(error)

        was_owner = chat.owner_id == command.user_id
        await self._uow.members.remove(command.chat_id, command.user_id)

        if was_owner:
            new_owner = await self._uow.members.find_oldest_active_excluding(
                command.chat_id, command.user_id
            )
            if new_owner is not None:
                await self._uow.members.update_role(new_owner.id, ChatMemberRole.owner)
                await self._uow.chats.update(
                    command.chat_id, ChatUpdate(owner_id=new_owner.user_id)
                )
            else:
                await self._uow.chats.update(
                    command.chat_id, ChatUpdate(is_archived=True)
                )

        await self._uow.commit()
        return Result.ok(None)
