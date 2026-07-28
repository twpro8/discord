from abc import ABC, abstractmethod

from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import (
    ChatRepository,
)
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)


class AbstractMessageUnitOfWork(ABC):
    messages: MessageRepository
    chats: ChatRepository
    chat_members: ChatMemberRepository
    channels: ChannelRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
