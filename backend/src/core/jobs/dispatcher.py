import asyncio
from collections.abc import Mapping
from typing import Any, Protocol

from celery import Celery

from src.core.jobs.task_names import JobTaskName


class JobDispatcher(Protocol):
    """Enqueue background work without the caller depending on Celery.

    Generic verb + enum name + mapping payload — same shape as
    `core.realtime.notifier.RealtimeNotifier.publish_to_room` — so a
    command handler can depend on this Protocol alone and the concrete
    execution mechanism (Celery today) can be swapped later with no
    change above this boundary. `payload` must stay primitive/plain data,
    same discipline as `Command` fields, enforced harder here since it
    crosses a real process boundary via broker serialization.
    """

    async def enqueue(
        self,
        task_name: JobTaskName,
        payload: Mapping[str, Any],
        *,
        queue: str = "default",
    ) -> str: ...


class CeleryJobDispatcher:
    """The only class outside `transport/tasks/` allowed to talk to Celery.

    `Celery.send_task` is a synchronous, blocking call (it just publishes
    to the broker, but still does blocking socket I/O) — run it in a
    thread so a command handler awaiting `enqueue` never blocks the event
    loop, keeping this Protocol's async contract genuinely non-blocking
    rather than only nominally async.
    """

    def __init__(self, celery_app: Celery) -> None:
        self._celery_app = celery_app

    async def enqueue(
        self,
        task_name: JobTaskName,
        payload: Mapping[str, Any],
        *,
        queue: str = "default",
    ) -> str:
        result = await asyncio.to_thread(
            self._celery_app.send_task,
            task_name,
            kwargs=dict(payload),
            queue=queue,
        )
        return str(result.id)
