from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.chats.domain.repositories.chat_unit_of_work import (
    AbstractChatUnitOfWork,
)
from src.modules.chats.infrastructure.persistence.repositories import (
    ChatMemberRepository,
    ChatRepository,
)
from src.shared.unit_of_work import BaseUnitOfWork


class ChatUnitOfWork(BaseUnitOfWork, AbstractChatUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ):
        super().__init__(session)
        self.chats = chat_repository
        self.members = chat_member_repository

    def _uow_marker(self) -> None: ...
