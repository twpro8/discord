from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.kernel.dependencies import SessionDep
from src.modules.channel.dependencies import ChannelRepositoryDep
from src.modules.chat.dependencies import ChatMemberRepositoryDep, ChatRepositoryDep
from src.modules.message.repository import MessageRepository
from src.modules.message.service import MessageService
from src.modules.message.unit_of_work import MessageUnitOfWork


def get_message_repository(session: SessionDep) -> MessageRepository:
    return MessageRepository(session)


async def get_message_unit_of_work(
    session: SessionDep,
    message_repository: MessageRepositoryDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
    channel_repository: ChannelRepositoryDep,
) -> AsyncGenerator[MessageUnitOfWork]:
    async with MessageUnitOfWork(
        session,
        message_repository,
        chat_repository,
        chat_member_repository,
        channel_repository,
    ) as message_unit_of_work:
        yield message_unit_of_work


def get_message_service(message_unit_of_work: MessageUnitOfWorkDep) -> MessageService:
    return MessageService(message_unit_of_work)


MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
MessageUnitOfWorkDep = Annotated[MessageUnitOfWork, Depends(get_message_unit_of_work)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
