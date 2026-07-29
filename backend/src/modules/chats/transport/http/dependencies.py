from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.chats.domain.repositories.chat_member_repository import (
    ChatMemberRepository,
)
from src.modules.chats.domain.repositories.chat_repository import ChatRepository
from src.modules.chats.infrastructure.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepositoryImpl(session)


def get_chat_member_repository(session: SessionDep) -> ChatMemberRepository:
    return ChatMemberRepositoryImpl(session)


ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
ChatMemberRepositoryDep = Annotated[
    ChatMemberRepository, Depends(get_chat_member_repository)
]
