import asyncio
from collections.abc import Coroutine
from typing import Any

from celery import Task

from src.core.logging import get_logger
from src.shared.errors import LumiereError, TransientError
from src.shared.result import Result

logger = get_logger(__name__)


def run_async[T](coro: Coroutine[Any, Any, T]) -> T:
    """Sync/async bridge for Celery's sync task entrypoints.

    A fresh event loop per call (via `asyncio.run`) is deliberate: it's
    what makes `get_null_pool_session_factory()` mandatory, not just
    preferred, for any DB session opened inside `coro` — a pooled
    `AsyncEngine`'s connections are bound to the loop that created them,
    and each `run_async` call gets a brand-new loop.
    """
    return asyncio.run(coro)


def handle_result(result: Result[Any, LumiereError], *, task: Task) -> None:
    """Classify a dispatched Command's Result for Celery retry purposes.

    Every `LumiereError` is a permanent failure by default — retrying a
    `NotFoundError`/`ConflictError`/`ValidationError` burns cycles for
    nothing and risks duplicate side effects on a non-idempotent task.
    Only `TransientError`, raised deliberately by a handler talking to
    flaky infrastructure, triggers a Celery retry.
    """
    if result.is_err:
        error = result.error
        if isinstance(error, TransientError):
            logger.warning(
                "task.transient_failure",
                task_name=task.name,
                task_id=task.request.id,
                error=str(error),
            )
            raise task.retry(exc=error)
        logger.error(
            "task.permanent_failure",
            task_name=task.name,
            task_id=task.request.id,
            error=str(error),
        )
        return
    logger.info("task.succeeded", task_name=task.name, task_id=task.request.id)
