from uuid import UUID

from src.core.realtime.manager import RoomMembershipUpdater
from src.modules.chats.domain import services
from src.modules.chats.domain.exceptions import (
    CannotRemoveSelfError,
    MemberNotFoundError,
)
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.usecases.realtime import leave_members_from_chat_room
from src.shared.domain.transaction import Transaction


class RemoveMemberUseCase:
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

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID, target_user_id: UUID
    ) -> None:
        await services.assert_is_group_chat_owner(
            self._chats, self._members, user_id, chat_id
        )

        if target_user_id == user_id:
            raise CannotRemoveSelfError

        target = await self._members.find_active(chat_id, target_user_id)
        if target is None:
            raise MemberNotFoundError

        await self._members.remove(chat_id, target_user_id)

        await self._tx.commit()
        await leave_members_from_chat_room(
            self._room_membership_updater, chat_id, [target_user_id]
        )
