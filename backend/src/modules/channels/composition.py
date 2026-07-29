from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
    CreateChannelCommandHandler,
)
from src.modules.channels.infrastructure.persistence.repository import (
    ChannelRepositoryImpl,
)
from src.modules.channels.infrastructure.unit_of_work import ChannelUnitOfWorkImpl
from src.shared.application.in_process_mediator import InProcessMediator


async def register_channel_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
) -> None:
    channel_repository = ChannelRepositoryImpl(session)
    uow = await stack.enter_async_context(
        ChannelUnitOfWorkImpl(session=session, channel_repository=channel_repository)
    )

    mediator.register_command(CreateChannelCommand, CreateChannelCommandHandler(uow))
