from dataclasses import dataclass
from uuid import UUID

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.chats.application.realtime import join_members_to_chat_room
from src.modules.chats.domain import services
from src.modules.chats.domain.entities.dtos import AddMemberResult, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole
from src.modules.chats.domain.exceptions import TargetUserNotFoundError
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.modules.users.public.facade import UsersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class AddMemberCommand(Command):
    chat_id: UUID
    user_id: UUID
    user_ids: list[UUID]


class AddMemberCommandHandler:
    def __init__(
        self,
        uow: ChatUnitOfWork,
        users_facade: UsersFacade,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._uow = uow
        self._users_facade = users_facade
        self._room_membership_updater = room_membership_updater

    async def handle(
        self, command: AddMemberCommand
    ) -> Result[AddMemberResult, LumiereError]:
        try:
            await services.assert_is_group_chat_owner(
                self._uow.chats, self._uow.members, command.user_id, command.chat_id
            )

            for target_id in command.user_ids:
                if not await self._users_facade.user_exists(target_id):
                    raise TargetUserNotFoundError

            active_ids = await self._uow.members.list_active_user_ids(command.chat_id)
        except LumiereError as error:
            return Result.err(error)

        to_add = [uid for uid in command.user_ids if uid not in active_ids]
        skipped = [uid for uid in command.user_ids if uid in active_ids]

        if to_add:
            await self._uow.members.add_members(
                [
                    MemberCreate(
                        user_id=uid,
                        chat_id=command.chat_id,
                        role=ChatMemberRole.member,
                    )
                    for uid in to_add
                ]
            )

        await self._uow.commit()
        await join_members_to_chat_room(
            self._room_membership_updater, command.chat_id, to_add
        )
        return Result.ok(AddMemberResult(added=to_add, skipped=skipped))
