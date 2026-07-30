from uuid import UUID

from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.exceptions import (
    ChatNotFoundError,
    NotChatMemberError,
    NotChatOwnerError,
)
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository


async def assert_is_chat_member(
    chats: ChatRepository,
    chat_members: ChatMemberRepository,
    user_id: UUID,
    chat_id: UUID,
) -> Chat:
    chat = await chats.find_by_id(chat_id)
    if chat is None:
        raise ChatNotFoundError

    membership = await chat_members.find_active(chat_id, user_id)
    if membership is None:
        raise NotChatMemberError

    return chat


async def assert_is_chat_owner(
    chats: ChatRepository,
    chat_members: ChatMemberRepository,
    user_id: UUID,
    chat_id: UUID,
) -> Chat:
    chat = await assert_is_chat_member(chats, chat_members, user_id, chat_id)
    if chat.owner_id != user_id:
        raise NotChatOwnerError
    return chat
