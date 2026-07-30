from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.infrastructure.persistence.repository import (
    ChannelRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
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
from src.modules.servers.infrastructure.persistence.server_member_repository_impl import (
    ServerMemberRepositoryImpl,
)
from src.shared.application.in_process_mediator import InProcessMediator


async def register_message_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
) -> None:
    message_repository = MessageRepositoryImpl(session)
    chat_repository = ChatRepositoryImpl(session)
    chat_member_repository = ChatMemberRepositoryImpl(session)
    channel_repository = ChannelRepositoryImpl(session)
    server_member_repository = ServerMemberRepositoryImpl(session)
    uow = await stack.enter_async_context(
        MessageUnitOfWorkImpl(
            session,
            message_repository,
            chat_repository,
            chat_member_repository,
            channel_repository,
            server_member_repository,
        )
    )

    mediator.register_command(
        SendChannelMessageCommand, SendChannelMessageCommandHandler(uow)
    )
    mediator.register_command(
        SendChatMessageCommand, SendChatMessageCommandHandler(uow)
    )
