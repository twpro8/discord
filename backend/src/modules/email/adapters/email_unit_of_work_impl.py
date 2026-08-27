from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.email.domain.repositories.email_message_repository import (
    EmailMessageRepository,
)
from src.modules.email.domain.repositories.email_unit_of_work import EmailUnitOfWork
from src.shared.data.unit_of_work import BaseUnitOfWork


class EmailUnitOfWorkImpl(BaseUnitOfWork, EmailUnitOfWork):
    email_messages: EmailMessageRepository

    def __init__(
        self,
        session: AsyncSession,
        email_message_repository: EmailMessageRepository,
    ) -> None:
        super().__init__(session)
        self.email_messages = email_message_repository

    def _uow_marker(self) -> None: ...
