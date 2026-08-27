from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.dtos import ChatUpdate, ChatUpdateData
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository


class UpdateChatUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._chats = chat_repository
        self._members = chat_member_repository

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID, update_data: ChatUpdateData
    ) -> Chat:
        await services.assert_is_group_chat_owner(
            self._chats, self._members, user_id, chat_id
        )
        return await self._chats.update(
            chat_id,
            ChatUpdate(
                name=update_data.name,
                description=update_data.description,
                image_url=update_data.image_url,
            ),
        )
