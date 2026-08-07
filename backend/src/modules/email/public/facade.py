from contextlib import AsyncExitStack
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.jobs import JobDispatcher
from src.modules.email.application.commands.send_email import (
    SendEmailCommand,
    SendEmailCommandHandler,
)
from src.modules.email.application.queries.get_email_status import (
    GetEmailStatusQuery,
    GetEmailStatusQueryHandler,
)
from src.modules.email.domain.entities.dtos import EmailMessageDTO
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.infrastructure.email_unit_of_work_impl import (
    EmailUnitOfWorkImpl,
)
from src.modules.email.infrastructure.persistence.email_message_repository_impl import (
    EmailMessageRepositoryImpl,
)
from src.shared.errors import LumiereError
from src.shared.result import Result


class EmailFacade(Protocol):
    """The only way other modules may reach `email`. Not wired into any
    consumer yet — see `composition.py`'s docstring — but this is the
    boundary a future consumer (`users`, `auth`, ...) will call."""

    async def send_email(
        self,
        *,
        to: str,
        template: EmailTemplateName,
        context: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> Result[EmailMessageDTO, LumiereError]: ...

    async def get_email_status(self, message_id: UUID) -> EmailMessageDTO | None: ...


class HandlerBackedEmailFacade:
    """Wraps handlers built against the *same* session as the caller.

    Deliberately not mediator-backed: this module has no HTTP router, and
    per AGENTS.md the mediator is for HTTP-triggered dispatch, not
    inter-module calls — same reasoning as `channels.public.facade.HandlerBackedChannelsFacade`.
    """

    def __init__(
        self,
        send_email_handler: SendEmailCommandHandler,
        get_email_status_handler: GetEmailStatusQueryHandler,
    ) -> None:
        self._send_email_handler = send_email_handler
        self._get_email_status_handler = get_email_status_handler

    async def send_email(
        self,
        *,
        to: str,
        template: EmailTemplateName,
        context: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> Result[EmailMessageDTO, LumiereError]:
        return await self._send_email_handler.handle(
            SendEmailCommand(
                to=to,
                template=template,
                context=context,
                idempotency_key=idempotency_key,
            )
        )

    async def get_email_status(self, message_id: UUID) -> EmailMessageDTO | None:
        result = await self._get_email_status_handler.handle(
            GetEmailStatusQuery(message_id=message_id)
        )
        if result.is_err:
            return None
        return result.value


async def build_email_facade(
    session: AsyncSession,
    stack: AsyncExitStack,
    job_dispatcher: JobDispatcher,
) -> EmailFacade:
    email_message_repository = EmailMessageRepositoryImpl(session)
    uow = await stack.enter_async_context(
        EmailUnitOfWorkImpl(
            session=session,
            email_message_repository=email_message_repository,
        )
    )
    return HandlerBackedEmailFacade(
        SendEmailCommandHandler(uow, job_dispatcher),
        GetEmailStatusQueryHandler(email_message_repository),
    )
