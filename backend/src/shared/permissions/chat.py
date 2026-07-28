from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from src.modules.chats.domain.exceptions import (
    ChatNotFoundError,
    NotChatMemberError,
    NotChatOwnerError,
)

if TYPE_CHECKING:
    from src.modules.chats.domain.entities.chat import Chat
    from src.modules.chats.domain.repositories.chat_member_repository import (
        ChatMemberRepository,
    )
    from src.modules.chats.domain.repositories.chat_repository import (
        ChatRepository,
    )


class SupportsChatPermissions(Protocol):
    chats: ChatRepository
    chat_members: ChatMemberRepository


async def assert_is_chat_member(
    uow: SupportsChatPermissions,
    user_id: UUID,
    chat_id: UUID,
) -> Chat:
    chat = await uow.chats.find_by_id(chat_id)
    if chat is None:
        raise ChatNotFoundError

    membership = await uow.chat_members.find_active(chat_id, user_id)
    if membership is None:
        raise NotChatMemberError

    return chat


async def assert_is_chat_owner(
    uow: SupportsChatPermissions,
    user_id: UUID,
    chat_id: UUID,
) -> Chat:
    chat = await assert_is_chat_member(uow, user_id, chat_id)
    if chat.owner_id != user_id:
        raise NotChatOwnerError
    return chat
