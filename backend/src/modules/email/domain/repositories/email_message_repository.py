from typing import Protocol
from uuid import UUID

from src.modules.email.domain.entities.dtos import EmailMessageCreate
from src.modules.email.domain.entities.email_message import EmailMessage


class EmailMessageRepository(Protocol):
    async def create(self, data: EmailMessageCreate) -> EmailMessage: ...

    async def find_by_id(self, message_id: UUID) -> EmailMessage | None: ...

    async def find_by_idempotency_key(
        self, idempotency_key: str
    ) -> EmailMessage | None: ...

    async def mark_sent(
        self, message_id: UUID, *, provider_message_id: str | None
    ) -> EmailMessage: ...

    async def mark_retrying(self, message_id: UUID, *, error: str) -> EmailMessage: ...

    async def mark_failed(self, message_id: UUID, *, error: str) -> EmailMessage: ...
