from contextlib import AsyncExitStack
from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
    CreateChannelCommandHandler,
)
from src.modules.channels.domain.entities.schemas import ChannelDTO
from src.modules.channels.infrastructure.channel_unit_of_work_impl import (
    ChannelUnitOfWorkImpl,
)
from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.shared.errors import LumiereError
from src.shared.result import Result


class ChannelsFacade(Protocol):
    async def create_default_channel(
        self, server_id: UUID
    ) -> Result[ChannelDTO, LumiereError]: ...


class HandlerBackedChannelsFacade:
    """Wraps a CreateChannelCommandHandler built against the *same* session
    as the caller, so a same-transaction, no-separate-commit delegation
    (e.g. servers creating a default channel while creating a server) still
    goes through this module's public boundary instead of the caller
    reaching into channels' application/infrastructure directly.

    Deliberately not mediator-backed: per CLAUDE.md, a command that needs
    another module's write behavior as part of its own atomic operation
    holds a handler instance built by its own composition, not a mediator
    dispatch — the mediator is for HTTP-triggered dispatch.
    """

    def __init__(self, create_channel_handler: CreateChannelCommandHandler) -> None:
        self._create_channel_handler = create_channel_handler

    async def create_default_channel(
        self, server_id: UUID
    ) -> Result[ChannelDTO, LumiereError]:
        result = await self._create_channel_handler.handle(
            CreateChannelCommand(server_id=server_id, name="general", is_commit=False)
        )
        if result.is_err:
            return Result.err(result.error)
        return Result.ok(ChannelDTO.model_validate(result.value))


async def build_channels_facade(
    session: AsyncSession, stack: AsyncExitStack
) -> ChannelsFacade:
    channel_repository = ChannelRepositoryImpl(session)
    uow = await stack.enter_async_context(
        ChannelUnitOfWorkImpl(session=session, channel_repository=channel_repository)
    )
    return HandlerBackedChannelsFacade(CreateChannelCommandHandler(uow))
