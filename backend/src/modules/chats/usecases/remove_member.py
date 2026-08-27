from uuid import UUID

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.chats.domain import services
from src.modules.chats.domain.exceptions import (
    CannotRemoveSelfError,
    MemberNotFoundError,
)
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.modules.chats.usecases.realtime import leave_members_from_chat_room


class RemoveMemberUseCase:
    def __init__(
        self, uow: ChatUnitOfWork, room_membership_updater: RoomMembershipUpdater
    ) -> None:
        self._uow = uow
        self._room_membership_updater = room_membership_updater

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID, target_user_id: UUID
    ) -> None:
        await services.assert_is_group_chat_owner(
            self._uow.chats, self._uow.members, user_id, chat_id
        )

        if target_user_id == user_id:
            raise CannotRemoveSelfError

        target = await self._uow.members.find_active(chat_id, target_user_id)
        if target is None:
            raise MemberNotFoundError

        await self._uow.members.remove(chat_id, target_user_id)

        await self._uow.commit()
        await leave_members_from_chat_room(
            self._room_membership_updater, chat_id, [target_user_id]
        )
