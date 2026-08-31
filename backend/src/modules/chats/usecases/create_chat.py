from uuid import UUID

from src.core.realtime.manager import RoomMembershipUpdater
from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.dtos import (
    ChatCreate,
    ChatCreateData,
    MemberCreate,
)
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import SelfChatForbiddenError
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.usecases.realtime import join_members_to_chat_room
from src.shared.domain.transaction import Transaction


class CreateChatUseCase:
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

    async def __call__(self, *, creator_id: UUID, data: ChatCreateData) -> Chat:
        if data.type == ChatType.private:
            return await self._get_or_create_private_chat(creator_id, data)
        return await self._create_group_chat(creator_id, data)

    async def _get_or_create_private_chat(
        self,
        creator_id: UUID,
        data: ChatCreateData,
    ) -> Chat:
        if creator_id == data.target_user_id:
            raise SelfChatForbiddenError

        assert data.target_user_id

        existing_chat = await self._chats.find_private_chat(
            user_a=creator_id,
            user_b=data.target_user_id,
        )
        if existing_chat:
            return existing_chat

        chat = await self._chats.create(ChatCreate(type=ChatType.private))

        member_ids = [creator_id, data.target_user_id]
        members = [
            MemberCreate(user_id=user_id, chat_id=chat.id) for user_id in member_ids
        ]

        await self._members.add_members(members)
        await self._tx.commit()
        await join_members_to_chat_room(
            self._room_membership_updater, chat.id, member_ids
        )

        return chat

    async def _create_group_chat(
        self,
        creator_id: UUID,
        data: ChatCreateData,
    ) -> Chat:
        chat = await self._chats.create(
            ChatCreate(
                owner_id=creator_id,
                type=ChatType.group,
                name=data.name,
                description=data.description,
            )
        )

        member_ids = list(data.member_ids) if data.member_ids else []
        members = [
            MemberCreate(
                user_id=user_id,
                chat_id=chat.id,
                role=ChatMemberRole.member,
            )
            for user_id in member_ids
        ]
        member_ids.append(creator_id)

        members.append(
            MemberCreate(
                user_id=creator_id,
                chat_id=chat.id,
                role=ChatMemberRole.owner,
            )
        )

        await self._members.add_members(members)
        await self._tx.commit()
        await join_members_to_chat_room(
            self._room_membership_updater, chat.id, member_ids
        )

        return chat
