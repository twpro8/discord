from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.adapters.channel_unit_of_work_impl import (
    ChannelUnitOfWorkImpl,
)
from src.modules.channels.adapters.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.channels.domain.entities.dtos import ChannelDTO, channel_to_dto
from src.modules.channels.usecases.create_channel import CreateChannelUseCase


class ChannelsFacade(Protocol):
    async def create_default_channel(self, server_id: UUID) -> ChannelDTO: ...


class UseCaseBackedChannelsFacade:
    """Wraps a CreateChannelUseCase built against the *same* session as the
    caller, so a same-transaction, no-separate-commit delegation (e.g.
    servers creating a default channel while creating a server) still
    goes through this module's public boundary instead of the caller
    reaching into channels' usecases/adapters directly.

    Deliberately not going through a shared dispatcher: per AGENTS.md, an
    operation that needs another module's write behavior as part of its
    own atomic operation holds a use-case instance built by its own
    composition, not a mediator/bus dispatch.
    """

    def __init__(self, create_channel_use_case: CreateChannelUseCase) -> None:
        self._create_channel = create_channel_use_case

    async def create_default_channel(self, server_id: UUID) -> ChannelDTO:
        channel = await self._create_channel(
            server_id=server_id, name="general", is_commit=False
        )
        return channel_to_dto(channel)


def build_channels_facade(session: AsyncSession) -> ChannelsFacade:
    channel_repository = ChannelRepositoryImpl(session)
    uow = ChannelUnitOfWorkImpl(session=session, channel_repository=channel_repository)
    return UseCaseBackedChannelsFacade(CreateChannelUseCase(uow))
