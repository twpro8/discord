from collections.abc import Mapping
from typing import Any

from src.core.jobs.dispatcher import CeleryJobDispatcher
from src.core.jobs.task_names import JobTaskName


class _FakeAsyncResult:
    def __init__(self, task_id: str) -> None:
        self.id = task_id


class FakeCeleryApp:
    """No broker, no Celery worker machinery — just enough of `Celery`'s
    `send_task` surface for `CeleryJobDispatcher` to run against."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, dict[str, Any], str]] = []

    def send_task(
        self, name: str, kwargs: Mapping[str, Any], queue: str
    ) -> _FakeAsyncResult:
        self.sent.append((name, dict(kwargs), queue))
        return _FakeAsyncResult(task_id="abc-123")


async def test_enqueue_sends_task_with_payload_and_queue() -> None:
    app = FakeCeleryApp()
    dispatcher = CeleryJobDispatcher(app)

    task_id = await dispatcher.enqueue(
        JobTaskName.PING, {"message": "hi"}, queue="notifications"
    )

    assert task_id == "abc-123"
    assert app.sent == [(JobTaskName.PING, {"message": "hi"}, "notifications")]


async def test_enqueue_defaults_to_default_queue() -> None:
    app = FakeCeleryApp()
    dispatcher = CeleryJobDispatcher(app)

    await dispatcher.enqueue(JobTaskName.PING, {})

    assert app.sent[0][2] == "default"
