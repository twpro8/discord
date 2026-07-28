from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.channels.transport.http.dependencies import ChannelRepositoryDep
from src.modules.chats.transport.http.dependencies import (
    ChatMemberRepositoryDep,
    ChatRepositoryDep,
)
from src.modules.messages.application.commands.send_channel_message import (
    SendChannelMessageCommand,
)
from src.modules.messages.application.commands.send_chat_message import (
    SendChatMessageCommand,
)
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.modules.messages.infrastructure.message_unit_of_work_impl import (
    MessageUnitOfWorkImpl,
)
from src.modules.messages.infrastructure.persistence.message_repository_impl import (
    MessageRepositoryImpl,
)


def get_message_repository(session: SessionDep) -> MessageRepository:
    return MessageRepositoryImpl(session)


async def get_message_unit_of_work(
    session: SessionDep,
    message_repository: MessageRepositoryDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    channel_repository: ChannelRepositoryDep,
) -> AsyncGenerator[MessageUnitOfWork]:
    async with MessageUnitOfWorkImpl(
        session,
        message_repository,
        chat_repository,
        chat_member_repository,
        channel_repository,
    ) as message_unit_of_work:
        yield message_unit_of_work


def get_send_channel_message_command(
    uow: MessageUnitOfWorkDep,
) -> SendChannelMessageCommand:
    return SendChannelMessageCommand(uow)


def get_send_chat_message_command(
    uow: MessageUnitOfWorkDep,
) -> SendChatMessageCommand:
    return SendChatMessageCommand(uow)


MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
MessageUnitOfWorkDep = Annotated[MessageUnitOfWork, Depends(get_message_unit_of_work)]
SendChannelMessageCommandDep = Annotated[
    SendChannelMessageCommand, Depends(get_send_channel_message_command)
]
SendChatMessageCommandDep = Annotated[
    SendChatMessageCommand, Depends(get_send_chat_message_command)
]
