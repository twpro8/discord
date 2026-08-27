from typing import Any
from uuid import UUID

from celery import Task

from src.core.config import settings
from src.core.database.session import get_null_pool_session_factory
from src.core.jobs.celery_app import celery_app
from src.core.jobs.runner import handle_task_error, run_async
from src.core.jobs.task_names import JobTaskName
from src.core.logging import get_logger
from src.modules.email.adapters.persistence.email_message_repository_impl import (
    EmailMessageRepositoryImpl,
)
from src.modules.email.adapters.providers.factory import build_email_provider
from src.modules.email.adapters.rendering.jinja_renderer import (
    JinjaTemplateRenderer,
)
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.usecases.deliver_email import DeliverEmailUseCase
from src.shared.data.transaction import SqlAlchemyTransaction
from src.shared.errors import LumiereError

logger = get_logger(__name__)


async def _deliver(
    *,
    message_id: str,
    to: str,
    template: str,
    context: dict[str, Any],
) -> None:
    """Self-composes its own session/transaction/renderer/provider — a
    Celery worker has no request-scoped DI container to reach into (see
    `core/jobs/runner.py`), so every task builds its dependencies inline
    rather than going through a shared facade. No auto-commit here (that's
    a FastAPI request-lifecycle thing): DeliverEmailUseCase commits
    explicitly at each of its branches."""
    session_factory = get_null_pool_session_factory()
    async with session_factory() as session:
        repository = EmailMessageRepositoryImpl(session)
        use_case = DeliverEmailUseCase(
            SqlAlchemyTransaction(session),
            repository,
            JinjaTemplateRenderer(),
            build_email_provider(settings),
        )
        await use_case(
            message_id=UUID(message_id),
            to=to,
            template=EmailTemplateName(template),
            context=context,
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
    try:
        run_async(
            _deliver(
                message_id=message_id,
                to=to,
                template=template,
                context=context,
            )
        )
    except LumiereError as error:
        handle_task_error(error, task=self)
        return
    logger.info("task.succeeded", task_name=self.name, task_id=self.request.id)
