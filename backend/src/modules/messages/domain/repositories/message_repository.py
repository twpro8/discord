from typing import Protocol

from src.modules.messages.domain.entities.dtos import MessageCreate
from src.modules.messages.domain.entities.message import Message


class MessageRepository(Protocol):
    async def create(self, data: MessageCreate) -> Message: ...
