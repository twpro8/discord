from dataclasses import dataclass
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
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class SendEmailCommand(Command):
    to: str
    template: EmailTemplateName
    context: dict[str, Any]
    idempotency_key: str | None = None


class SendEmailCommandHandler:
    """Producer side — runs in the caller's request-scoped session/UoW.
    Records a PENDING `EmailMessage` and hands the actual delivery off to
    Celery via `JobDispatcher`; never talks to SMTP itself (see
    `DeliverEmailCommandHandler`, which the worker-side task runs)."""

    def __init__(
        self,
        email_unit_of_work: EmailUnitOfWork,
        job_dispatcher: JobDispatcher,
    ) -> None:
        self._uow = email_unit_of_work
        self._job_dispatcher = job_dispatcher

    async def handle(
        self, command: SendEmailCommand
    ) -> Result[EmailMessageDTO, LumiereError]:
        if command.idempotency_key is not None:
            existing = await self._uow.email_messages.find_by_idempotency_key(
                command.idempotency_key
            )
            if existing is not None:
                return Result.ok(email_message_to_dto(existing))

        try:
            address = EmailAddress(command.to)
        except LumiereError as error:
            return Result.err(error)

        message = await self._uow.email_messages.create(
            EmailMessageCreate(
                idempotency_key=command.idempotency_key,
                to=str(address),
                template=command.template,
                context=dict(command.context),
            )
        )
        await self._uow.commit()

        await self._job_dispatcher.enqueue(
            JobTaskName.SEND_EMAIL,
            {
                "message_id": str(message.id),
                "to": str(address),
                "template": command.template.value,
                "context": dict(command.context),
            },
        )

        return Result.ok(email_message_to_dto(message))
