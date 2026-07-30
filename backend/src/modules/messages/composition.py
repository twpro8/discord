from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.chats.public.facade import build_chats_facade
from src.modules.messages.application.commands.send_channel_message import (
    SendChannelMessageCommand,
    SendChannelMessageCommandHandler,
)
from src.modules.messages.application.commands.send_chat_message import (
    SendChatMessageCommand,
    SendChatMessageCommandHandler,
)
from src.modules.messages.infrastructure.message_unit_of_work_impl import (
    MessageUnitOfWorkImpl,
)
from src.modules.messages.infrastructure.persistence.message_repository_impl import (
    MessageRepositoryImpl,
)
from src.modules.servers.public.facade import build_servers_facade
from src.shared.application.in_process_mediator import InProcessMediator


async def register_message_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
) -> None:
    message_repository = MessageRepositoryImpl(session)
    chat_repository = ChatRepositoryImpl(session)
    channel_repository = ChannelRepositoryImpl(session)
    uow = await stack.enter_async_context(
        MessageUnitOfWorkImpl(
            session,
            message_repository,
            chat_repository,
            channel_repository,
        )
    )

    chats_facade = build_chats_facade(session)
    servers_facade = build_servers_facade(session)

    mediator.register_command(
        SendChannelMessageCommand,
        SendChannelMessageCommandHandler(uow, servers_facade),
    )
    mediator.register_command(
        SendChatMessageCommand, SendChatMessageCommandHandler(uow, chats_facade)
    )
