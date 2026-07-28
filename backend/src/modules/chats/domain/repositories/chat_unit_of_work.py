from abc import ABC, abstractmethod

from src.modules.chats.domain.repositories.chat_repository import (
    ChatMemberRepository,
    ChatRepository,
)


class AbstractChatUnitOfWork(ABC):
    chats: ChatRepository
    members: ChatMemberRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
