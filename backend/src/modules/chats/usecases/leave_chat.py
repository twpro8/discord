from uuid import UUID

from src.core.realtime.manager import RoomMembershipUpdater
from src.modules.chats.domain import services
from src.modules.chats.domain.entities.dtos import ChatUpdate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import CannotLeavePrivateChatError
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.usecases.realtime import leave_members_from_chat_room
from src.shared.domain.transaction import Transaction


class LeaveChatUseCase:
    def __init__(
        self,
        tx: Transaction,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._tx = tx
        self._chats = chat_repository
        self._members = chat_member_repository
        self._room_membership_updater = room_membership_updater

    async def __call__(self, *, chat_id: UUID, user_id: UUID) -> None:
        chat = await services.assert_is_chat_member(
            self._chats, self._members, user_id, chat_id
        )
        if chat.type == ChatType.private:
            raise CannotLeavePrivateChatError

        was_owner = chat.owner_id == user_id
        await self._members.remove(chat_id, user_id)

        if was_owner:
            new_owner = await self._members.find_oldest_active_excluding(
                chat_id, user_id
            )
            if new_owner is not None:
                await self._members.update_role(new_owner.id, ChatMemberRole.owner)
                await self._chats.update(
                    chat_id, ChatUpdate(owner_id=new_owner.user_id)
                )
            else:
                await self._chats.update(chat_id, ChatUpdate(is_archived=True))

        await self._tx.commit()
        await leave_members_from_chat_room(
            self._room_membership_updater, chat_id, [user_id]
        )
