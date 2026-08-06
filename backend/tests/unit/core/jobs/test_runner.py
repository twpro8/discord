from dataclasses import dataclass
from typing import Any

import pytest

from src.core.jobs.runner import handle_result
from src.core.jobs.task_names import JobTaskName
from src.shared.errors import NotFoundError, TransientError
from src.shared.result import Result


class RetrySignal(Exception):
    """Stands in for Celery's own Retry exception, which `Task.retry`
    raises internally — the fake below raises this instead so tests can
    assert `handle_result` propagates it without depending on Celery's
    worker machinery."""


@dataclass
class _FakeRequest:
    id: str = "task-id-123"


class FakeTask:
    """No DB, no HTTP, no broker — just enough of Celery's `Task` surface
    (`.name`, `.request.id`, `.retry`) for `handle_result` to run against."""

    def __init__(self) -> None:
        self.name = JobTaskName.PING
        self.request = _FakeRequest()
        self.retried_with: BaseException | None = None

    def retry(self, *, exc: BaseException) -> Any:
        self.retried_with = exc
        raise RetrySignal(exc)


def test_handle_result_ok_does_not_retry() -> None:
    task = FakeTask()

    handle_result(Result.ok("done"), task=task)

    assert task.retried_with is None


def test_handle_result_transient_error_retries() -> None:
    task = FakeTask()
    error = TransientError()

    with pytest.raises(RetrySignal):
        handle_result(Result.err(error), task=task)

    assert task.retried_with is error


def test_handle_result_permanent_error_does_not_retry() -> None:
    task = FakeTask()
    error = NotFoundError()

    handle_result(Result.err(error), task=task)

    assert task.retried_with is None
