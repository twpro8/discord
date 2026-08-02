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
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.mediator import Mediator


def _build_uow(services: RequestServices) -> MessageUnitOfWorkImpl:
    return MessageUnitOfWorkImpl(
        services.session,
        MessageRepositoryImpl(services.session),
        ChatRepositoryImpl(services.session),
        ChannelRepositoryImpl(services.session),
    )


def _build_send_channel_message_handler(
    services: RequestServices, _mediator: Mediator
) -> SendChannelMessageCommandHandler:
    servers_facade = build_servers_facade(services.session)
    return SendChannelMessageCommandHandler(_build_uow(services), servers_facade)


def _build_send_chat_message_handler(
    services: RequestServices, _mediator: Mediator
) -> SendChatMessageCommandHandler:
    chats_facade = build_chats_facade(services.session)
    return SendChatMessageCommandHandler(
        _build_uow(services), chats_facade, services.realtime_notifier
    )


def _build_edit_message_handler(
    services: RequestServices, _mediator: Mediator
) -> EditMessageCommandHandler:
    return EditMessageCommandHandler(_build_uow(services))


def _build_delete_message_handler(
    services: RequestServices, _mediator: Mediator
) -> DeleteMessageCommandHandler:
    chats_facade = build_chats_facade(services.session)
    servers_facade = build_servers_facade(services.session)
    return DeleteMessageCommandHandler(
        _build_uow(services), chats_facade, servers_facade
    )


def _build_list_chat_messages_handler(
    services: RequestServices, _mediator: Mediator
) -> ListChatMessagesQueryHandler:
    chats_facade = build_chats_facade(services.session)
    return ListChatMessagesQueryHandler(
        MessageRepositoryImpl(services.session), chats_facade
    )


def _build_list_channel_messages_handler(
    services: RequestServices, _mediator: Mediator
) -> ListChannelMessagesQueryHandler:
    servers_facade = build_servers_facade(services.session)
    return ListChannelMessagesQueryHandler(_build_uow(services), servers_facade)


def register_message_handlers(registry: HandlerRegistry) -> None:
    registry.register_command_factory(
        SendChannelMessageCommand, _build_send_channel_message_handler
    )
    registry.register_command_factory(
        SendChatMessageCommand, _build_send_chat_message_handler
    )
    registry.register_command_factory(EditMessageCommand, _build_edit_message_handler)
    registry.register_command_factory(
        DeleteMessageCommand, _build_delete_message_handler
    )

    registry.register_query_factory(
        ListChatMessagesQuery, _build_list_chat_messages_handler
    )
    registry.register_query_factory(
        ListChannelMessagesQuery, _build_list_channel_messages_handler
    )
