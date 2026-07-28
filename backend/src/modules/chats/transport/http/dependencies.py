from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.chats.application.commands.create_chat import CreateChatCommand
from src.modules.chats.application.queries.get_chats import GetChatsQuery
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.domain.repositories.chat_unit_of_work import (
    ChatUnitOfWork,
)
from src.modules.chats.infrastructure.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.chats.infrastructure.unit_of_work import ChatUnitOfWorkImpl


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepositoryImpl(session)


def get_chat_member_repository(session: SessionDep) -> ChatMemberRepository:
    return ChatMemberRepositoryImpl(session)


def get_create_chat_command(uow: ChatUnitOfWorkDep) -> CreateChatCommand:
    return CreateChatCommand(uow)


def get_chats_query(chat_repository: ChatRepositoryDep) -> GetChatsQuery:
    return GetChatsQuery(chat_repository)


async def get_chat_unit_of_work(
    session: SessionDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepositoryDep,
) -> AsyncGenerator[ChatUnitOfWork]:
    async with ChatUnitOfWorkImpl(
        session=session,
        chat_repository=chat_repository,
        chat_member_repository=chat_member_repository,
    ) as unit_of_work:
        yield unit_of_work


ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
ChatMemberRepositoryDep = Annotated[
    ChatMemberRepository, Depends(get_chat_member_repository)
]
ChatUnitOfWorkDep = Annotated[ChatUnitOfWorkImpl, Depends(get_chat_unit_of_work)]
CreateChatCommandDep = Annotated[CreateChatCommand, Depends(get_create_chat_command)]
GetChatsQueryDep = Annotated[GetChatsQuery, Depends(get_chats_query)]
