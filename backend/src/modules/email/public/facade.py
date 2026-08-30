from typing import Any, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.jobs import JobDispatcher
from src.modules.email.adapters.persistence.email_message_repository_impl import (
    EmailMessageRepositoryImpl,
)
from src.modules.email.domain.entities.dtos import EmailMessageDTO
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.exceptions import EmailMessageNotFoundError
from src.modules.email.usecases.get_email_status import GetEmailStatusUseCase
from src.modules.email.usecases.send_email import SendEmailUseCase
from src.shared.adapters.transaction import SqlAlchemyTransaction


class EmailFacade(Protocol):
    """The only way other modules may reach `email`. Not wired into any
    consumer yet — see `send_email_task.py`'s docstring — but this is the
    boundary a future consumer (`users`, `auth`, ...) will call."""

    async def send_email(
        self,
        *,
        to: str,
        template: EmailTemplateName,
        context: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> EmailMessageDTO: ...

    async def get_email_status(self, message_id: UUID) -> EmailMessageDTO | None: ...


class UseCaseBackedEmailFacade:
    """Wraps use cases built against the *same* session as the caller.

    Deliberately not going through a shared dispatcher: this module has
    no HTTP router, and other modules should reach it only through this
    facade — same reasoning as
    `channels.public.facade.UseCaseBackedChannelsFacade`."""

    def __init__(
        self,
        send_email_use_case: SendEmailUseCase,
        get_email_status_use_case: GetEmailStatusUseCase,
    ) -> None:
        self._send_email = send_email_use_case
        self._get_email_status = get_email_status_use_case

    async def send_email(
        self,
        *,
        to: str,
        template: EmailTemplateName,
        context: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> EmailMessageDTO:
        return await self._send_email(
            to=to,
            template=template,
            context=context,
            idempotency_key=idempotency_key,
        )

    async def get_email_status(self, message_id: UUID) -> EmailMessageDTO | None:
        try:
            return await self._get_email_status(message_id=message_id)
        except EmailMessageNotFoundError:
            return None


def build_email_facade(
    session: AsyncSession,
    job_dispatcher: JobDispatcher,
) -> EmailFacade:
    email_message_repository = EmailMessageRepositoryImpl(session)
    tx = SqlAlchemyTransaction(session)
    return UseCaseBackedEmailFacade(
        SendEmailUseCase(tx, email_message_repository, job_dispatcher),
        GetEmailStatusUseCase(email_message_repository),
    )
