from typing import Any
from uuid import UUID

from src.core.config import settings
from src.modules.email.domain.entities.dtos import (
    EmailMessageDTO,
    OutboundEmail,
    email_message_to_dto,
)
from src.modules.email.domain.enums import EmailStatus, EmailTemplateName
from src.modules.email.domain.exceptions import EmailMessageNotFoundError
from src.modules.email.domain.gateways.email_provider import EmailProvider
from src.modules.email.domain.gateways.template_renderer import TemplateRenderer
from src.modules.email.domain.repositories.email_message_repository import (
    EmailMessageRepository,
)
from src.shared.domain.transaction import Transaction
from src.shared.errors import LumiereError, TransientError


class DeliverEmailUseCase:
    """Consumer side — self-composed and run by `transport/tasks/send_email_task.py`
    inside a Celery task's own short-lived session/transaction, outside the
    FastAPI request lifecycle — so unlike a request-scoped use case, nothing
    auto-commits here. Every branch below commits explicitly."""

    def __init__(
        self,
        tx: Transaction,
        email_message_repository: EmailMessageRepository,
        template_renderer: TemplateRenderer,
        email_provider: EmailProvider,
    ) -> None:
        self._tx = tx
        self._email_messages = email_message_repository
        self._renderer = template_renderer
        self._provider = email_provider

    async def __call__(
        self,
        *,
        message_id: UUID,
        to: str,
        template: EmailTemplateName,
        context: dict[str, Any],
    ) -> EmailMessageDTO:
        message = await self._email_messages.get_by_id(message_id)
        if message is None:
            raise EmailMessageNotFoundError

        if message.status == EmailStatus.SENT:
            # At-least-once redelivery of the same task for an
            # already-sent message — safe no-op, not a failure.
            return email_message_to_dto(message)

        try:
            rendered = await self._renderer.render(template, context)
        except LumiereError as error:
            await self._email_messages.mark_failed(message.id, error=str(error))
            await self._tx.commit()
            raise

        outbound = OutboundEmail(
            to=to,
            from_email=settings.EMAILS_FROM_EMAIL,
            from_name=settings.EMAILS_FROM_NAME,
            subject=rendered.subject,
            html_body=rendered.html_body,
            text_body=rendered.text_body,
        )

        try:
            receipt = await self._provider.send(outbound)
        except TransientError as error:
            await self._email_messages.mark_retrying(message.id, error=str(error))
            await self._tx.commit()
            raise
        except LumiereError as error:
            await self._email_messages.mark_failed(message.id, error=str(error))
            await self._tx.commit()
            raise

        updated = await self._email_messages.mark_sent(
            message.id, provider_message_id=receipt.provider_message_id
        )
        await self._tx.commit()
        return email_message_to_dto(updated)
