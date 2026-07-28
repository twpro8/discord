from typing import Protocol

from src.modules.messages.domain.entities.schemas import Message, MessageCreate


class MessageRepository(Protocol):
    async def create(self, data: MessageCreate) -> Message: ...
