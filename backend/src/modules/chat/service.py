from uuid import UUID

from src.core.services.base_service import BaseService
from src.modules.chat.enums import ChatMemberRole, ChatType
from src.modules.chat.exceptions import SelfChatForbiddenError
from src.modules.chat.schemas import (
    Chat,
    ChatCreate,
    ChatCreateRequest,
    ChatSummaryPage,
    MemberCreate,
)
from src.modules.chat.unit_of_work import ChatUnitOfWork


class ChatService(BaseService):
    def __init__(self, uow: ChatUnitOfWork):
        self.uow = uow

    async def create_chat(
        self,
        creator_id: UUID,
        data: ChatCreateRequest,
    ) -> Chat:
        if data.type == ChatType.private:
            return await self._get_or_create_private_chat(creator_id, data)
        else:
            return await self._create_group_chat(creator_id, data)

    async def _get_or_create_private_chat(
        self,
        creator_id: UUID,
        data: ChatCreateRequest,
    ) -> Chat:
        if creator_id == data.target_user_id:
            raise SelfChatForbiddenError

        assert data.target_user_id

        # get chat between
        existing_chat = await self.uow.chats.find_private_chat(
            user_a=creator_id,
            user_b=data.target_user_id,
        )
        if existing_chat:
            return existing_chat

        chat = await self.uow.chats.create(ChatCreate(type=ChatType.private))

        members = [
            MemberCreate(
                user_id=creator_id,
                chat_id=chat.id,
            ),
            MemberCreate(
                user_id=data.target_user_id,
                chat_id=chat.id,
            ),
        ]

        await self.uow.members.add_members(members)
        await self.uow.commit()

        return chat

    async def _create_group_chat(
        self,
        creator_id: UUID,
        data: ChatCreateRequest,
    ) -> Chat:
        chat = await self.uow.chats.create(
            ChatCreate(
                owner_id=creator_id,
                type=ChatType.group,
                name=data.name,
                description=data.description,
            )
        )

        members = []

        if data.member_ids:
            members = [
                MemberCreate(
                    user_id=user_id,
                    chat_id=chat.id,
                    role=ChatMemberRole.member,
                )
                for user_id in data.member_ids
            ]

        members.append(
            MemberCreate(
                user_id=creator_id,
                chat_id=chat.id,
                role=ChatMemberRole.owner,
            )
        )

        await self.uow.members.add_members(members)
        await self.uow.commit()

        return chat

    async def get_chats(
        self,
        user_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> ChatSummaryPage:
        return await self.uow.chats.list_chats_for_user(user_id, limit, cursor)
