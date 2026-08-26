from uuid import UUID

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.chats.domain import services
from src.modules.chats.domain.entities.dtos import ChatUpdate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import CannotLeavePrivateChatError
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.modules.chats.usecases.realtime import leave_members_from_chat_room


class LeaveChatUseCase:
    def __init__(
        self, uow: ChatUnitOfWork, room_membership_updater: RoomMembershipUpdater
    ) -> None:
        self._uow = uow
        self._room_membership_updater = room_membership_updater

    async def __call__(self, *, chat_id: UUID, user_id: UUID) -> None:
        chat = await services.assert_is_chat_member(
            self._uow.chats, self._uow.members, user_id, chat_id
        )
        if chat.type == ChatType.private:
            raise CannotLeavePrivateChatError

        was_owner = chat.owner_id == user_id
        await self._uow.members.remove(chat_id, user_id)

        if was_owner:
            new_owner = await self._uow.members.find_oldest_active_excluding(
                chat_id, user_id
            )
            if new_owner is not None:
                await self._uow.members.update_role(new_owner.id, ChatMemberRole.owner)
                await self._uow.chats.update(
                    chat_id, ChatUpdate(owner_id=new_owner.user_id)
                )
            else:
                await self._uow.chats.update(chat_id, ChatUpdate(is_archived=True))

        await self._uow.commit()
        await leave_members_from_chat_room(
            self._room_membership_updater, chat_id, [user_id]
        )
