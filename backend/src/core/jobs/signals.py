from typing import Any

from celery import Task
from celery.signals import task_postrun, task_prerun
from structlog.contextvars import bind_contextvars, clear_contextvars


@task_prerun.connect  # type: ignore[untyped-decorator]
def bind_task_logging_context(task_id: str, task: Task, **_kwargs: Any) -> None:
    """Tag every log line emitted during this task with its id/name.

    `configure_logging()` already wires `structlog.contextvars.merge_contextvars`
    into the processor chain, but nothing calls `bind_contextvars` anywhere
    else in the codebase yet — this is that mechanism's first real
    consumer, not a new pattern. Without it, concurrent tasks interleaving
    in one worker's stdout are effectively unattributable.

    `**_kwargs` swallows the rest of Celery's signal payload (`sender`,
    `args`, `kwargs`, ...) — required so the receiver doesn't reject
    fields it doesn't care about, not an unused parameter left in by
    mistake.
    """
    bind_contextvars(task_id=task_id, task_name=task.name)


@task_postrun.connect  # type: ignore[untyped-decorator]
def clear_task_logging_context(**_kwargs: Any) -> None:
    clear_contextvars()
