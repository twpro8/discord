from abc import ABC, abstractmethod

from src.modules.email.domain.repositories.email_message_repository import (
    EmailMessageRepository,
)


class EmailUnitOfWork(ABC):
    email_messages: EmailMessageRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
