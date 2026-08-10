"""Regression coverage for a real bug: api/v1/ws.py's disconnect handler
used to call `asyncio.create_task(...)` without keeping a reference to the
result. Per Python's own asyncio docs, the event loop only holds a *weak*
reference to a task — with nothing else referencing it, the task can be
garbage-collected before it runs to completion. In production this meant a
closed tab could sometimes leave a user showing "online" indefinitely
(not just until the next PresenceSweeper pass), since the detached
mark_connection_offline task never got a chance to finish. Fixed via
`_fire_and_forget`, which tracks the task in a module-level set until it's
done — these tests cover that tracking mechanism directly.
"""

import asyncio

from src.api.v1.ws import _background_tasks, _fire_and_forget


async def test_fire_and_forget_tracks_the_task_until_it_completes() -> None:
    started = asyncio.Event()
    finish = asyncio.Event()

    async def work() -> None:
        started.set()
        await finish.wait()

    _fire_and_forget(work())
    await started.wait()

    assert len(_background_tasks) == 1

    finish.set()
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert _background_tasks == set()


async def test_fire_and_forget_runs_the_coroutine_to_completion() -> None:
    completed = False

    async def work() -> None:
        nonlocal completed
        await asyncio.sleep(0)
        completed = True

    _fire_and_forget(work())

    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert completed


async def test_fire_and_forget_does_not_leak_tasks_across_multiple_calls() -> None:
    async def work() -> None:
        return None

    for _ in range(5):
        _fire_and_forget(work())

    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert _background_tasks == set()
