from abc import ABC, abstractmethod

from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import (
    ChatRepository,
)


class ChatUnitOfWork(ABC):
    chats: ChatRepository
    members: ChatMemberRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
