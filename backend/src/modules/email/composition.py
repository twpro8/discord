from contextlib import AsyncExitStack

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
from src.modules.email.infrastructure.email_unit_of_work_impl import (
    EmailUnitOfWorkImpl,
)
from src.modules.email.infrastructure.persistence.email_message_repository_impl import (
    EmailMessageRepositoryImpl,
)
from src.shared.application.in_process_mediator import InProcessMediator


async def register_email_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
    job_dispatcher: JobDispatcher,
) -> None:
    """Written for structural completeness/unit-test symmetry with every
    other module's `composition.py`, but deliberately NOT called from
    `api/v1/dependencies.py::get_mediator` yet: `email` has no HTTP router
    and no consumer module wired in. Wiring this call in (plus adding an
    `email_facade` param to a real consumer's own `composition.py`, the
    same way `auth`'s takes `users_facade`) is a future integration task,
    not part of preparing this module."""
    email_message_repository = EmailMessageRepositoryImpl(session)
    uow = await stack.enter_async_context(
        EmailUnitOfWorkImpl(
            session=session,
            email_message_repository=email_message_repository,
        )
    )

    mediator.register_command(
        SendEmailCommand,
        SendEmailCommandHandler(uow, job_dispatcher),
    )
    mediator.register_query(
        GetEmailStatusQuery,
        GetEmailStatusQueryHandler(email_message_repository),
    )
