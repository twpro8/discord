from uuid import UUID

from src.modules.email.domain.entities.dtos import EmailMessageDTO, email_message_to_dto
from src.modules.email.domain.exceptions import EmailMessageNotFoundError
from src.modules.email.domain.repositories.email_message_repository import (
    EmailMessageRepository,
)


class GetEmailStatusUseCase:
    def __init__(self, email_message_repository: EmailMessageRepository) -> None:
        self._email_messages = email_message_repository

    async def __call__(self, *, message_id: UUID) -> EmailMessageDTO:
        message = await self._email_messages.find_by_id(message_id)
        if message is None:
            raise EmailMessageNotFoundError
        return email_message_to_dto(message)
