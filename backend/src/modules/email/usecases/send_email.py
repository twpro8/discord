from typing import Any

from src.core.jobs import JobDispatcher, JobTaskName
from src.modules.email.domain.entities.dtos import (
    EmailMessageCreate,
    EmailMessageDTO,
    email_message_to_dto,
)
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.repositories.email_message_repository import (
    EmailMessageRepository,
)
from src.shared.domain.transaction import Transaction


class SendEmailUseCase:
    """Producer side — runs in the caller's request-scoped session.
    Records a PENDING `EmailMessage` and hands the actual delivery off to
    Celery via `JobDispatcher`; never talks to SMTP itself (see
    `DeliverEmailUseCase`, which the worker-side task runs)."""

    def __init__(
        self,
        tx: Transaction,
        email_message_repository: EmailMessageRepository,
        job_dispatcher: JobDispatcher,
    ) -> None:
        self._tx = tx
        self._email_messages = email_message_repository
        self._job_dispatcher = job_dispatcher

    async def __call__(
        self,
        *,
        to: str,
        template: EmailTemplateName,
        context: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> EmailMessageDTO:
        if idempotency_key is not None:
            existing = await self._email_messages.find_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                return email_message_to_dto(existing)

        to = to.strip().lower()

        message = await self._email_messages.create(
            EmailMessageCreate(
                idempotency_key=idempotency_key,
                to=to,
                template=template,
                context=dict(context),
            )
        )
        await self._tx.commit()

        await self._job_dispatcher.enqueue(
            JobTaskName.SEND_EMAIL,
            {
                "message_id": str(message.id),
                "to": to,
                "template": template.value,
                "context": dict(context),
            },
        )

        return email_message_to_dto(message)
