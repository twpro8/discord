from abc import ABC, abstractmethod

from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)


class ChannelUnitOfWork(ABC):
    channels: ChannelRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
