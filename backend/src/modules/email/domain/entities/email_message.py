from datetime import datetime
from typing import Any
from uuid import UUID

from src.modules.email.domain.enums import EmailStatus, EmailTemplateName
from src.shared.domain.entity import Entity


class EmailMessage(Entity):
    """The delivery ledger row for a single send attempt. Status transitions
    (PENDING/RETRYING -> SENT|FAILED) are performed by
    `EmailMessageRepository.mark_sent`/`mark_retrying`/`mark_failed`
    (narrow, SQL-level operations — same pattern as
    `MessageRepository.update_body`/`soft_delete`), not by mutating this
    object in place."""

    def __init__(
        self,
        id: UUID,
        idempotency_key: str | None,
        to: str,
        template: EmailTemplateName,
        context: dict[str, Any],
        status: EmailStatus,
        attempts: int,
        error_message: str | None,
        provider_message_id: str | None,
        created_at: datetime,
        updated_at: datetime,
        sent_at: datetime | None,
    ) -> None:
        super().__init__(id)
        self.idempotency_key = idempotency_key
        self.to = to
        self.template = template
        self.context = context
        self.status = status
        self.attempts = attempts
        self.error_message = error_message
        self.provider_message_id = provider_message_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.sent_at = sent_at
