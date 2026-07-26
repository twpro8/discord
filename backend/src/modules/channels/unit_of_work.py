from sqlalchemy.ext.asyncio import AsyncSession

from src.kernel.unit_of_work.base_unit_of_work import BaseUnitOfWork
from src.modules.channels.repository import ChannelRepository


class ChannelUnitOfWork(BaseUnitOfWork):
    channels: ChannelRepository

    def __init__(
        self,
        session: AsyncSession,
        channel_repository: ChannelRepository,
    ) -> None:
        super().__init__(session)
        self.channels = channel_repository

    def _uow_marker(self) -> None: ...
