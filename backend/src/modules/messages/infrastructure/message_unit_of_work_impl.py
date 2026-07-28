from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.shared.unit_of_work import BaseUnitOfWork


class MessageUnitOfWorkImpl(BaseUnitOfWork, MessageUnitOfWork):
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
