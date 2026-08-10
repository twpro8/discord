import asyncio
import contextlib

from src.core.logging import get_logger
from src.modules.presence.application.presence_service import PresenceService

logger = get_logger(__name__)


class PresenceSweeper:
    """Crash self-healing: periodically purges stale connections (ones
    whose heartbeat stopped without a clean disconnect — e.g. a hard-killed
    process) and fans out any resulting offline transitions. Own background
    asyncio task, started/stopped in main.py's lifespan alongside
    RedisSubscriptionManager — same shape, not registered on the mediator
    for the same reason PresenceService itself isn't (see its docstring).

    If deployed with more than one backend instance, every instance's
    sweeper independently scans the same shared Redis state, so duplicate
    (idempotent) offline fan-outs can occur under concurrent instances —
    acceptable for this app's current single-process Compose deployment.
    """

    def __init__(
        self,
        presence_service: PresenceService,
        *,
        interval_seconds: float,
    ) -> None:
        self._presence_service = presence_service
        self._interval_seconds = interval_seconds
        self._task: asyncio.Task[None] | None = None
        self._stopped = True

    def start(self) -> None:
        self._stopped = False
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stopped = True
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def _run(self) -> None:
        while not self._stopped:
            try:
                await asyncio.sleep(self._interval_seconds)
                await self._presence_service.sweep_stale()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("presence.sweep_iteration_failed")
