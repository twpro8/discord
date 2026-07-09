from uuid import UUID
from typing import Protocol, TYPE_CHECKING

from src.chat.exceptions import NotChatMemberError, NotChatOwnerError, ChatNotFoundError

if TYPE_CHECKING:
    from src.chat.schemas import Chat
    from src.chat.repositories import ChatRepository, ChatMemberRepository


class SupportsChatPermissions(Protocol):
    chats: ChatRepository
    chat_members: ChatMemberRepository


async def assert_is_chat_member(
    uow: SupportsChatPermissions,
    user_id: UUID,
    chat_id: UUID,
) -> Chat:
    chat = await uow.chats.get_by_id(chat_id)
    if chat is None:
        raise ChatNotFoundError

    membership = await uow.chat_members.get_active(chat_id, user_id)
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
