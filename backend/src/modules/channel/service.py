from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.base_service import BaseService
from src.modules.channel.enums import ChannelType
from src.modules.channel.schemas import ChannelCreateSchema, ChannelSchema
from src.modules.channel.unit_of_work import ChannelUnitOfWork


class ChannelService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        channel_unit_of_work: ChannelUnitOfWork,
    ) -> None:
        super().__init__(session)
        self.uow = channel_unit_of_work

    async def create_channel(
        self,
        server_id: UUID,
        name: str,
        type: ChannelType = ChannelType.text,
        topic: str | None = None,
        is_private: bool = False,
        is_commit: bool = True,
    ) -> ChannelSchema:
        channel_data = ChannelCreateSchema(
            server_id=server_id,
            name=name,
            type=type,
            position=0,
            topic=topic,
            is_private=is_private,
        )

        channel = await self.uow.channels.create(channel_data)
        if is_commit:
            await self.uow.commit()

        return channel
