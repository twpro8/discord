from dataclasses import dataclass
from uuid import UUID

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.chats.application.realtime import leave_members_from_chat_room
from src.modules.chats.domain import services
from src.modules.chats.domain.exceptions import (
    CannotRemoveSelfError,
    MemberNotFoundError,
)
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class RemoveMemberCommand(Command):
    chat_id: UUID
    user_id: UUID
    target_user_id: UUID


class RemoveMemberCommandHandler:
    def __init__(
        self, uow: ChatUnitOfWork, room_membership_updater: RoomMembershipUpdater
    ) -> None:
        self._uow = uow
        self._room_membership_updater = room_membership_updater

    async def handle(self, command: RemoveMemberCommand) -> Result[None, LumiereError]:
        try:
            await services.assert_is_group_chat_owner(
                self._uow.chats, self._uow.members, command.user_id, command.chat_id
            )

            if command.target_user_id == command.user_id:
                raise CannotRemoveSelfError

            target = await self._uow.members.find_active(
                command.chat_id, command.target_user_id
            )
            if target is None:
                raise MemberNotFoundError

            await self._uow.members.remove(command.chat_id, command.target_user_id)
        except LumiereError as error:
            return Result.err(error)

        await self._uow.commit()
        await leave_members_from_chat_room(
            self._room_membership_updater, command.chat_id, [command.target_user_id]
        )
        return Result.ok(None)
