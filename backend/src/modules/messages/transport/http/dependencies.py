from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import (
    RealtimeNotifierDep,
    RoomMembershipUpdaterDep,
    SessionDep,
)
from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.chats.public.facade import ChatsFacade, build_chats_facade
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.modules.messages.infrastructure.message_unit_of_work_impl import (
    MessageUnitOfWorkImpl,
)
from src.modules.messages.infrastructure.persistence.message_repository_impl import (
    MessageRepositoryImpl,
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


async def get_message_unit_of_work(
    session: SessionDep,
) -> AsyncGenerator[MessageUnitOfWork]:
    message_repository = MessageRepositoryImpl(session)
    chat_repository = ChatRepositoryImpl(session)
    channel_repository = ChannelRepositoryImpl(session)
    async with MessageUnitOfWorkImpl(
        session,
        message_repository,
        chat_repository,
        channel_repository,
    ) as uow:
        yield uow


async def get_chats_facade(session: SessionDep) -> ChatsFacade:
    return build_chats_facade(session)


async def get_servers_facade(session: SessionDep) -> ServersFacade:
    return build_servers_facade(session)


MessageUnitOfWorkDep = Annotated[MessageUnitOfWork, Depends(get_message_unit_of_work)]
ChatsFacadeDep = Annotated[ChatsFacade, Depends(get_chats_facade)]
ServersFacadeDep = Annotated[ServersFacade, Depends(get_servers_facade)]


async def get_send_channel_message_use_case(
    uow: MessageUnitOfWorkDep, servers_facade: ServersFacadeDep
) -> SendChannelMessageUseCase:
    return SendChannelMessageUseCase(uow, servers_facade)


async def get_send_chat_message_use_case(
    uow: MessageUnitOfWorkDep,
    chats_facade: ChatsFacadeDep,
    realtime_notifier: RealtimeNotifierDep,
) -> SendChatMessageUseCase:
    return SendChatMessageUseCase(uow, chats_facade, realtime_notifier)


async def get_edit_message_use_case(
    uow: MessageUnitOfWorkDep,
) -> EditMessageUseCase:
    return EditMessageUseCase(uow)


async def get_delete_message_use_case(
    uow: MessageUnitOfWorkDep,
    chats_facade: ChatsFacadeDep,
    servers_facade: ServersFacadeDep,
) -> DeleteMessageUseCase:
    return DeleteMessageUseCase(uow, chats_facade, servers_facade)


async def get_list_channel_messages_use_case(
    uow: MessageUnitOfWorkDep, servers_facade: ServersFacadeDep
) -> ListChannelMessagesUseCase:
    return ListChannelMessagesUseCase(uow, servers_facade)


async def get_list_chat_messages_use_case(
    uow: MessageUnitOfWorkDep,
    chats_facade: ChatsFacadeDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> ListChatMessagesUseCase:
    return ListChatMessagesUseCase(uow.messages, chats_facade, room_membership_updater)


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
