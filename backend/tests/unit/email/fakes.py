from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.modules.email.domain.entities.dtos import (
    EmailMessageCreate,
    OutboundEmail,
    ProviderReceipt,
    RenderedEmailContent,
)
from src.modules.email.domain.entities.email_message import EmailMessage
from src.modules.email.domain.enums import EmailStatus, EmailTemplateName


class FakeEmailMessageRepository:
    def __init__(self) -> None:
        self.messages: dict[UUID, EmailMessage] = {}

    async def create(self, data: EmailMessageCreate) -> EmailMessage:
        if data.idempotency_key is not None:
            for existing in self.messages.values():
                if existing.idempotency_key == data.idempotency_key:
                    return existing
        now = datetime.now(UTC)
        message = EmailMessage(
            id=uuid4(),
            idempotency_key=data.idempotency_key,
            to=data.to,
            template=data.template,
            context=dict(data.context),
            status=EmailStatus.PENDING,
            attempts=0,
            error_message=None,
            provider_message_id=None,
            created_at=now,
            updated_at=now,
            sent_at=None,
        )
        self.messages[message.id] = message
        return message

    async def get_by_id(self, message_id: UUID) -> EmailMessage | None:
        return self.messages.get(message_id)

    async def find_by_idempotency_key(
        self, idempotency_key: str
    ) -> EmailMessage | None:
        for message in self.messages.values():
            if message.idempotency_key == idempotency_key:
                return message
        return None

    async def mark_sent(
        self, message_id: UUID, *, provider_message_id: str | None
    ) -> EmailMessage:
        message = self.messages[message_id]
        message.status = EmailStatus.SENT
        message.attempts += 1
        message.provider_message_id = provider_message_id
        message.error_message = None
        message.sent_at = datetime.now(UTC)
        return message

    async def mark_retrying(self, message_id: UUID, *, error: str) -> EmailMessage:
        message = self.messages[message_id]
        message.status = EmailStatus.RETRYING
        message.attempts += 1
        message.error_message = error
        return message

    async def mark_failed(self, message_id: UUID, *, error: str) -> EmailMessage:
        message = self.messages[message_id]
        message.status = EmailStatus.FAILED
        message.attempts += 1
        message.error_message = error
        return message


class FakeTemplateRenderer:
    """Renders deterministically from the raw context, no Jinja2/disk I/O —
    a handler test only needs to assert the renderer/provider were called
    with the right arguments, not exercise real template files (see
    `tests/unit/email/test_jinja_renderer.py` for that)."""

    def __init__(self) -> None:
        self.calls: list[tuple[EmailTemplateName, dict[str, Any]]] = []

    async def render(
        self, template: EmailTemplateName, context: Mapping[str, Any]
    ) -> RenderedEmailContent:
        self.calls.append((template, dict(context)))
        return RenderedEmailContent(
            subject="Test subject",
            html_body="<p>Test body</p>",
            text_body="Test body",
        )


class FakeEmailProvider:
    def __init__(self, *, error: Exception | None = None) -> None:
        self.error = error
        self.sent: list[OutboundEmail] = []

    async def send(self, message: OutboundEmail) -> ProviderReceipt:
        if self.error is not None:
            raise self.error
        self.sent.append(message)
        return ProviderReceipt(provider_message_id="provider-message-id")
