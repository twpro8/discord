from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.channels.infrastructure.persistence.repository import (
    ChannelRepositoryImpl,
)


def get_channel_repository(session: SessionDep) -> ChannelRepository:
    return ChannelRepositoryImpl(session)


ChannelRepositoryDep = Annotated[ChannelRepository, Depends(get_channel_repository)]
