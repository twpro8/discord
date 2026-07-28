from typing import Protocol

from pydantic import BaseModel

from src.modules.messages.domain.entities.schemas import Message


class MessageRepository(Protocol):
    async def create(self, data: BaseModel) -> Message: ...
