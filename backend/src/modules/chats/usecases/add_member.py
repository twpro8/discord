from uuid import UUID

from src.core.realtime.manager import RoomMembershipUpdater
from src.modules.chats.domain import services
from src.modules.chats.domain.entities.dtos import AddMemberResult, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole
from src.modules.chats.domain.exceptions import TargetUserNotFoundError
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.usecases.realtime import join_members_to_chat_room
from src.modules.users.public.facade import UsersFacade
from src.shared.domain.transaction import Transaction


class AddMemberUseCase:
    def __init__(
        self,
        tx: Transaction,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
        users_facade: UsersFacade,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._tx = tx
        self._chats = chat_repository
        self._members = chat_member_repository
        self._users_facade = users_facade
        self._room_membership_updater = room_membership_updater

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID, user_ids: list[UUID]
    ) -> AddMemberResult:
        await services.assert_is_group_chat_owner(
            self._chats, self._members, user_id, chat_id
        )

        for target_id in user_ids:
            if not await self._users_facade.user_exists(target_id):
                raise TargetUserNotFoundError

        active_ids = await self._members.list_active_user_ids(chat_id)

        to_add = [uid for uid in user_ids if uid not in active_ids]
        skipped = [uid for uid in user_ids if uid in active_ids]

        if to_add:
            await self._members.add_members(
                [
                    MemberCreate(
                        user_id=uid,
                        chat_id=chat_id,
                        role=ChatMemberRole.member,
                    )
                    for uid in to_add
                ]
            )

        await self._tx.commit()
        await join_members_to_chat_room(self._room_membership_updater, chat_id, to_add)
        return AddMemberResult(added=to_add, skipped=skipped)
