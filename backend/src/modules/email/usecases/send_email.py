from typing import Any

from src.core.jobs import JobDispatcher, JobTaskName
from src.modules.email.domain.entities.dtos import (
    EmailMessageCreate,
    EmailMessageDTO,
    email_message_to_dto,
)
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.repositories.email_unit_of_work import EmailUnitOfWork
from src.modules.email.domain.value_objects.email_address import EmailAddress


class SendEmailUseCase:
    """Producer side — runs in the caller's request-scoped session/UoW.
    Records a PENDING `EmailMessage` and hands the actual delivery off to
    Celery via `JobDispatcher`; never talks to SMTP itself (see
    `DeliverEmailUseCase`, which the worker-side task runs)."""

    def __init__(
        self,
        email_unit_of_work: EmailUnitOfWork,
        job_dispatcher: JobDispatcher,
    ) -> None:
        self._uow = email_unit_of_work
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
            existing = await self._uow.email_messages.find_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                return email_message_to_dto(existing)

        address = EmailAddress(to)

        message = await self._uow.email_messages.create(
            EmailMessageCreate(
                idempotency_key=idempotency_key,
                to=str(address),
                template=template,
                context=dict(context),
            )
        )
        await self._uow.commit()

        await self._job_dispatcher.enqueue(
            JobTaskName.SEND_EMAIL,
            {
                "message_id": str(message.id),
                "to": str(address),
                "template": template.value,
                "context": dict(context),
            },
        )

        return email_message_to_dto(message)
