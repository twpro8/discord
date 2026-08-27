from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import (
    RealtimeNotifierDep,
    RoomMembershipUpdaterDep,
    SessionDep,
    TransactionDep,
)
from src.modules.channels.adapters.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.chats.adapters.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.public.facade import ChatsFacade, build_chats_facade
from src.modules.messages.adapters.persistence.message_repository_impl import (
    MessageRepositoryImpl,
)
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)
from src.modules.messages.usecases.delete_message import DeleteMessageUseCase
from src.modules.messages.usecases.edit_message import EditMessageUseCase
from src.modules.messages.usecases.list_channel_messages import (
    ListChannelMessagesUseCase,
)
from src.modules.messages.usecases.list_chat_messages import ListChatMessagesUseCase
from src.modules.messages.usecases.send_channel_message import (
    SendChannelMessageUseCase,
)
from src.modules.messages.usecases.send_chat_message import SendChatMessageUseCase
from src.modules.servers.public.facade import ServersFacade, build_servers_facade


def get_message_repository(session: SessionDep) -> MessageRepository:
    return MessageRepositoryImpl(session)


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepositoryImpl(session)


def get_channel_repository(session: SessionDep) -> ChannelRepository:
    return ChannelRepositoryImpl(session)


async def get_chats_facade(session: SessionDep) -> ChatsFacade:
    return build_chats_facade(session)


async def get_servers_facade(session: SessionDep) -> ServersFacade:
    return build_servers_facade(session)


MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
ChannelRepositoryDep = Annotated[ChannelRepository, Depends(get_channel_repository)]
ChatsFacadeDep = Annotated[ChatsFacade, Depends(get_chats_facade)]
ServersFacadeDep = Annotated[ServersFacade, Depends(get_servers_facade)]


async def get_send_channel_message_use_case(
    message_repository: MessageRepositoryDep,
    channel_repository: ChannelRepositoryDep,
    servers_facade: ServersFacadeDep,
    _tx: TransactionDep,
) -> SendChannelMessageUseCase:
    return SendChannelMessageUseCase(
        message_repository, channel_repository, servers_facade
    )


async def get_send_chat_message_use_case(
    tx: TransactionDep,
    message_repository: MessageRepositoryDep,
    chat_repository: ChatRepositoryDep,
    chats_facade: ChatsFacadeDep,
    realtime_notifier: RealtimeNotifierDep,
) -> SendChatMessageUseCase:
    return SendChatMessageUseCase(
        tx, message_repository, chat_repository, chats_facade, realtime_notifier
    )


async def get_edit_message_use_case(
    message_repository: MessageRepositoryDep,
    _tx: TransactionDep,
) -> EditMessageUseCase:
    return EditMessageUseCase(message_repository)


async def get_delete_message_use_case(
    message_repository: MessageRepositoryDep,
    channel_repository: ChannelRepositoryDep,
    chats_facade: ChatsFacadeDep,
    servers_facade: ServersFacadeDep,
    _tx: TransactionDep,
) -> DeleteMessageUseCase:
    return DeleteMessageUseCase(
        message_repository, channel_repository, chats_facade, servers_facade
    )


async def get_list_channel_messages_use_case(
    message_repository: MessageRepositoryDep,
    channel_repository: ChannelRepositoryDep,
    servers_facade: ServersFacadeDep,
) -> ListChannelMessagesUseCase:
    return ListChannelMessagesUseCase(
        message_repository, channel_repository, servers_facade
    )


async def get_list_chat_messages_use_case(
    message_repository: MessageRepositoryDep,
    chats_facade: ChatsFacadeDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> ListChatMessagesUseCase:
    return ListChatMessagesUseCase(
        message_repository, chats_facade, room_membership_updater
    )


SendChannelMessageUseCaseDep = Annotated[
    SendChannelMessageUseCase, Depends(get_send_channel_message_use_case)
]
SendChatMessageUseCaseDep = Annotated[
    SendChatMessageUseCase, Depends(get_send_chat_message_use_case)
]
EditMessageUseCaseDep = Annotated[
    EditMessageUseCase, Depends(get_edit_message_use_case)
]
DeleteMessageUseCaseDep = Annotated[
    DeleteMessageUseCase, Depends(get_delete_message_use_case)
]
ListChannelMessagesUseCaseDep = Annotated[
    ListChannelMessagesUseCase, Depends(get_list_channel_messages_use_case)
]
ListChatMessagesUseCaseDep = Annotated[
    ListChatMessagesUseCase, Depends(get_list_chat_messages_use_case)
]
