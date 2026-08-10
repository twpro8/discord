from typing import Any
from uuid import UUID

from celery import Task

from src.core.config import settings
from src.core.database.session import get_null_pool_session_factory
from src.core.jobs.celery_app import celery_app
from src.core.jobs.runner import handle_result, run_async
from src.core.jobs.task_names import JobTaskName
from src.modules.email.application.commands.deliver_email import (
    DeliverEmailCommand,
    DeliverEmailCommandHandler,
)
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.infrastructure.email_unit_of_work_impl import (
    EmailUnitOfWorkImpl,
)
from src.modules.email.infrastructure.persistence.email_message_repository_impl import (
    EmailMessageRepositoryImpl,
)
from src.modules.email.infrastructure.providers.factory import build_email_provider
from src.modules.email.infrastructure.rendering.jinja_renderer import (
    JinjaTemplateRenderer,
)
from src.shared.errors import LumiereError
from src.shared.result import Result


async def _deliver(
    *,
    message_id: str,
    to: str,
    template: str,
    context: dict[str, Any],
) -> Result[Any, LumiereError]:
    """Self-composes its own session/UoW/renderer/provider — a Celery
    worker has no request-scoped DI container to reach into (see
    `core/jobs/runner.py`), so every task builds its dependencies inline
    rather than going through `composition.py`/the mediator."""
    session_factory = get_null_pool_session_factory()
    async with session_factory() as session:
        repository = EmailMessageRepositoryImpl(session)
        async with EmailUnitOfWorkImpl(
            session=session,
            email_message_repository=repository,
        ) as uow:
            handler = DeliverEmailCommandHandler(
                uow,
                JinjaTemplateRenderer(),
                build_email_provider(settings),
            )
            return await handler.handle(
                DeliverEmailCommand(
                    message_id=UUID(message_id),
                    to=to,
                    template=EmailTemplateName(template),
                    context=context,
                )
            )


@celery_app.task(name=JobTaskName.SEND_EMAIL, bind=True)  # type: ignore[untyped-decorator]
def send_email_task(
    self: Task,
    *,
    message_id: str,
    to: str,
    template: str,
    context: dict[str, Any],
) -> None:
    result = run_async(
        _deliver(
            message_id=message_id,
            to=to,
            template=template,
            context=context,
        )
    )
    handle_result(result, task=self)
