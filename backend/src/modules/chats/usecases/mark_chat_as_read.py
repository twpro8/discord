from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository


class MarkChatAsReadUseCase:
    def __init__(
        self,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._chats = chat_repository
        self._members = chat_member_repository

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID, up_to_sequence: int | None = None
    ) -> None:
        chat = await services.assert_is_chat_member(
            self._chats, self._members, user_id, chat_id
        )

        target = up_to_sequence if up_to_sequence is not None else chat.last_sequence
        await self._members.update_last_read_seq(chat_id, user_id, target)
