from sqlalchemy.ext.asyncio import AsyncSession

from src.channel.repository import ChannelRepository
from src.chat.repositories import ChatMemberRepository, ChatRepository
from src.core.unit_of_work import BaseUnitOfWork
from src.message.repository import MessageRepository


class MessageUnitOfWork(BaseUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        message_repository: MessageRepository,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
        channel_repository: ChannelRepository,
    ) -> None:
        super().__init__(session)
        self.messages = message_repository
        self.chats = chat_repository
        self.chat_members = chat_member_repository
        self.channels = channel_repository

    def _uow_marker(self) -> None: ...
