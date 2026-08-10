from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from src.modules.email.domain.entities.email_message import EmailMessage
from src.modules.email.domain.enums import EmailStatus, EmailTemplateName


@dataclass(frozen=True, kw_only=True)
class EmailMessageCreate:
    """Persistence create payload — primitive fields only, matching the
    `email_messages` table columns (status/attempts default server-side)."""

    idempotency_key: str | None
    to: str
    template: EmailTemplateName
    context: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class EmailMessageDTO:
    """Facade/read-model DTO — what `EmailFacade` returns to future callers."""

    id: UUID
    to: str
    template: EmailTemplateName
    status: EmailStatus
    attempts: int
    error_message: str | None
    provider_message_id: str | None
    created_at: datetime
    updated_at: datetime
    sent_at: datetime | None


def email_message_to_dto(message: EmailMessage) -> EmailMessageDTO:
    return EmailMessageDTO(
        id=message.id,
        to=str(message.to),
        template=message.template,
        status=message.status,
        attempts=message.attempts,
        error_message=message.error_message,
        provider_message_id=message.provider_message_id,
        created_at=message.created_at,
        updated_at=message.updated_at,
        sent_at=message.sent_at,
    )


@dataclass(frozen=True, kw_only=True)
class RenderedEmailContent:
    """Output of the `TemplateRenderer` port."""

    subject: str
    html_body: str
    text_body: str | None


@dataclass(frozen=True, kw_only=True)
class OutboundEmail:
    """Input to the `EmailProvider` port — a fully composed, ready-to-send
    message. Kept separate from `EmailMessage` (the persisted ledger row)
    since a provider adapter has no business knowing about idempotency
    keys or delivery status."""

    to: str
    from_email: str
    from_name: str
    subject: str
    html_body: str
    text_body: str | None


@dataclass(frozen=True, kw_only=True)
class ProviderReceipt:
    """Output of the `EmailProvider` port on a successful send."""

    provider_message_id: str | None
