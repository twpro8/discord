from uuid import UUID

from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.schemas import (
    ChatCreate,
    ChatCreateRequest,
    MemberCreate,
)
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import SelfChatForbiddenError
from src.modules.chats.domain.repositories.chat_unit_of_work import (
    AbstractChatUnitOfWork,
)


class CreateChatCommand:
    def __init__(self, uow: AbstractChatUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, creator_id: UUID, data: ChatCreateRequest) -> Chat:
        if data.type == ChatType.private:
            return await self._get_or_create_private_chat(creator_id, data)
        return await self._create_group_chat(creator_id, data)

    async def _get_or_create_private_chat(
        self,
        creator_id: UUID,
        data: ChatCreateRequest,
    ) -> Chat:
        if creator_id == data.target_user_id:
            raise SelfChatForbiddenError

        assert data.target_user_id

        existing_chat = await self._uow.chats.find_private_chat(
            user_a=creator_id,
            user_b=data.target_user_id,
        )
        if existing_chat:
            return existing_chat

        chat = await self._uow.chats.create(ChatCreate(type=ChatType.private))

        members = [
            MemberCreate(user_id=creator_id, chat_id=chat.id),
            MemberCreate(user_id=data.target_user_id, chat_id=chat.id),
        ]

        await self._uow.members.add_members(members)
        await self._uow.commit()

        return chat

    async def _create_group_chat(
        self,
        creator_id: UUID,
        data: ChatCreateRequest,
    ) -> Chat:
        chat = await self._uow.chats.create(
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

        await self._uow.members.add_members(members)
        await self._uow.commit()

        return chat
