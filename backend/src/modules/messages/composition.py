from sqlalchemy.ext.asyncio import AsyncSession

from src.core.realtime.notifier import RealtimeNotifier
from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.chats.public.facade import build_chats_facade
from src.modules.messages.application.commands.delete_message import (
    DeleteMessageCommand,
    DeleteMessageCommandHandler,
)
from src.modules.messages.application.commands.edit_message import (
    EditMessageCommand,
    EditMessageCommandHandler,
)
from src.modules.messages.application.commands.send_channel_message import (
    SendChannelMessageCommand,
    SendChannelMessageCommandHandler,
)
from src.modules.messages.application.commands.send_chat_message import (
    SendChatMessageCommand,
    SendChatMessageCommandHandler,
)
from src.modules.messages.application.queries.list_channel_messages import (
    ListChannelMessagesQuery,
    ListChannelMessagesQueryHandler,
)
from src.modules.messages.application.queries.list_chat_messages import (
    ListChatMessagesQuery,
    ListChatMessagesQueryHandler,
)
from src.modules.messages.infrastructure.message_unit_of_work_impl import (
    MessageUnitOfWorkImpl,
)
from src.modules.messages.infrastructure.persistence.message_repository_impl import (
    MessageRepositoryImpl,
)
from src.modules.servers.public.facade import build_servers_facade
from src.shared.application.in_process_mediator import InProcessMediator


def register_message_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    realtime_notifier: RealtimeNotifier,
) -> None:
    message_repository = MessageRepositoryImpl(session)
    chat_repository = ChatRepositoryImpl(session)
    channel_repository = ChannelRepositoryImpl(session)
    uow = MessageUnitOfWorkImpl(
        session,
        message_repository,
        chat_repository,
        channel_repository,
    )

    chats_facade = build_chats_facade(session)
    servers_facade = build_servers_facade(session)

    mediator.register_command(
        SendChannelMessageCommand,
        SendChannelMessageCommandHandler(uow, servers_facade),
    )
    mediator.register_command(
        SendChatMessageCommand,
        SendChatMessageCommandHandler(uow, chats_facade, realtime_notifier),
    )
    mediator.register_command(EditMessageCommand, EditMessageCommandHandler(uow))
    mediator.register_command(
        DeleteMessageCommand,
        DeleteMessageCommandHandler(uow, chats_facade, servers_facade),
    )

    mediator.register_query(
        ListChatMessagesQuery,
        ListChatMessagesQueryHandler(message_repository, chats_facade),
    )
    mediator.register_query(
        ListChannelMessagesQuery,
        ListChannelMessagesQueryHandler(uow, servers_facade),
    )
