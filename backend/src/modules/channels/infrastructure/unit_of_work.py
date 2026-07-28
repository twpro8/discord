from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)
from src.shared.unit_of_work import BaseUnitOfWork


class ChannelUnitOfWorkImpl(BaseUnitOfWork, ChannelUnitOfWork):
    channels: ChannelRepository

    def __init__(
        self,
        session: AsyncSession,
        channel_repository: ChannelRepository,
    ) -> None:
        super().__init__(session)
        self.channels = channel_repository

    def _uow_marker(self) -> None: ...
