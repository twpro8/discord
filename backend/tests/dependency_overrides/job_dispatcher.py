from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from src.core.jobs import JobDispatcher, JobTaskName


class FakeJobDispatcher:
    """Records enqueue calls instead of touching a real broker.

    Same shape as `tests.unit.messages.fakes.FakeRealtimeNotifier`: no
    Celery import, no Redis — a handler test injects this directly and
    asserts on `.calls`.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[JobTaskName, dict[str, Any], str]] = []

    async def enqueue(
        self,
        task_name: JobTaskName,
        payload: Mapping[str, Any],
        *,
        queue: str = "default",
    ) -> str:
        self.calls.append((task_name, dict(payload), queue))
        return str(uuid4())


def get_test_job_dispatcher() -> JobDispatcher:
    return FakeJobDispatcher()
