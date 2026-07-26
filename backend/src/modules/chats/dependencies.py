from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.kernel.dependencies import SessionDep
from src.modules.chats.repositories import ChatMemberRepository, ChatRepository
from src.modules.chats.service import ChatService
from src.modules.chats.unit_of_work import ChatUnitOfWork


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepository(session)


def get_chat_member_repository(session: SessionDep) -> ChatMemberRepository:
    return ChatMemberRepository(session)


def get_chat_service(unit_of_work: ChatUnitOfWorkDep) -> ChatService:
    return ChatService(unit_of_work)


async def get_chat_unit_of_work(
    session: SessionDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
) -> AsyncGenerator[ChatUnitOfWork]:
    async with ChatUnitOfWork(
        session=session,
        chat_repository=chat_repository,
        chat_member_repository=chat_member_repository,
    ) as unit_of_work:
        yield unit_of_work


ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
ChatMemberRepositoryDep = Annotated[
    ChatMemberRepository, Depends(get_chat_member_repository)
]
ChatUnitOfWorkDep = Annotated[ChatUnitOfWork, Depends(get_chat_unit_of_work)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
