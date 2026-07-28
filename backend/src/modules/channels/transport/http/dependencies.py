from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
)
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)
from src.modules.channels.infrastructure.persistence.repository import (
    ChannelRepositoryImpl,
)
from src.modules.channels.infrastructure.unit_of_work import ChannelUnitOfWorkImpl


def get_channel_repository(session: SessionDep) -> ChannelRepository:
    return ChannelRepositoryImpl(session)


async def get_channel_unit_of_work(
    session: SessionDep,
    channel_repository: ChannelRepositoryDep,
) -> AsyncGenerator[ChannelUnitOfWork]:
    async with ChannelUnitOfWorkImpl(
        session=session,
        channel_repository=channel_repository,
    ) as channel_unit_of_work:
        yield channel_unit_of_work


def get_create_channel_command(
    channel_unit_of_work: ChannelUnitOfWorkDep,
) -> CreateChannelCommand:
    return CreateChannelCommand(channel_unit_of_work)


ChannelRepositoryDep = Annotated[ChannelRepository, Depends(get_channel_repository)]
CreateChannelCommandDep = Annotated[
    CreateChannelCommand, Depends(get_create_channel_command)
]
ChannelUnitOfWorkDep = Annotated[ChannelUnitOfWork, Depends(get_channel_unit_of_work)]
