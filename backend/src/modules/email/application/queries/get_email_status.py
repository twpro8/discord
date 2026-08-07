from dataclasses import dataclass
from uuid import UUID

from src.modules.email.domain.entities.dtos import EmailMessageDTO, email_message_to_dto
from src.modules.email.domain.exceptions import EmailMessageNotFoundError
from src.modules.email.domain.repositories.email_message_repository import (
    EmailMessageRepository,
)
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetEmailStatusQuery(Query):
    message_id: UUID


class GetEmailStatusQueryHandler:
    def __init__(self, email_message_repository: EmailMessageRepository) -> None:
        self._email_messages = email_message_repository

    async def handle(
        self, query: GetEmailStatusQuery
    ) -> Result[EmailMessageDTO, LumiereError]:
        message = await self._email_messages.find_by_id(query.message_id)
        if message is None:
            return Result.err(EmailMessageNotFoundError())
        return Result.ok(email_message_to_dto(message))
