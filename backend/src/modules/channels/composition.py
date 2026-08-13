from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
    CreateChannelCommandHandler,
)
from src.modules.channels.application.commands.delete_channel import (
    DeleteChannelCommand,
    DeleteChannelCommandHandler,
)
from src.modules.channels.application.commands.update_channel import (
    UpdateChannelCommand,
    UpdateChannelCommandHandler,
)
from src.modules.channels.infrastructure.channel_unit_of_work_impl import (
    ChannelUnitOfWorkImpl,
)
from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.application.in_process_mediator import InProcessMediator


async def register_channel_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
    servers_facade: ServersFacade,
) -> None:
    channel_repository = ChannelRepositoryImpl(session)
    uow = await stack.enter_async_context(
        ChannelUnitOfWorkImpl(session=session, channel_repository=channel_repository)
    )

    mediator.register_command(CreateChannelCommand, CreateChannelCommandHandler(uow))
    mediator.register_command(
        UpdateChannelCommand, UpdateChannelCommandHandler(uow, servers_facade)
    )
    mediator.register_command(
        DeleteChannelCommand, DeleteChannelCommandHandler(uow, servers_facade)
    )
