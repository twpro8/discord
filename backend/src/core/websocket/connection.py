import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID, uuid4

from src.core.logging import get_logger
from src.core.realtime.envelope import Envelope

logger = get_logger(__name__)


class SendableWebSocket(Protocol):
    """The subset of Starlette's WebSocket that Connection needs to send
    frames — kept narrow so tests can fake it without a real ASGI socket.
    """

    async def send_text(self, data: str) -> None: ...

    async def close(self, code: int = 1000, reason: str | None = None) -> None: ...


DisconnectCallback = Callable[["Connection"], Awaitable[None]]
"""Invoked when a connection must be torn down because it can no longer be
written to — either its send queue overflowed (too-slow consumer) or the
underlying socket write raised. Named generically since both cases mean
the same thing to the caller: disconnect this connection."""


class Connection:
    """A wrapper around one open WebSocket, decoupled from the raw send
    path via a bounded queue + dedicated writer task, so a slow client can
    never block the event loop shared with other connections/handlers.

    The reader loop (pulling client->server frames) is intentionally NOT
    owned here — ConnectionManager spawns and owns it, keeping Connection
    a pure send-side primitive.
    """

    __slots__ = (
        "connection_id",
        "user_id",
        "websocket",
        "rooms",
        "metadata",
        "connected_at",
        "last_seen_at",
        "_queue",
        "_writer_task",
        "_on_disconnect_needed",
        "_closed",
    )

    def __init__(
        self,
        websocket: SendableWebSocket,
        user_id: UUID,
        *,
        queue_maxsize: int,
        on_disconnect_needed: DisconnectCallback,
    ) -> None:
        self.connection_id: UUID = uuid4()
        self.user_id = user_id
        self.websocket = websocket
        self.rooms: set[str] = set()
        self.metadata: dict[str, Any] = {}
        self.connected_at = datetime.now(UTC)
        self.last_seen_at = self.connected_at
        self._queue: asyncio.Queue[Envelope] = asyncio.Queue(maxsize=queue_maxsize)
        self._on_disconnect_needed = on_disconnect_needed
        self._closed = False
        self._writer_task = asyncio.create_task(self._write_loop())

    def touch(self) -> None:
        """Record client activity (e.g. an inbound frame seen by the
        reader loop owned by ConnectionManager)."""
        self.last_seen_at = datetime.now(UTC)

    async def send(self, envelope: Envelope) -> None:
        """Enqueue an envelope for delivery; never writes to the socket
        directly. On a full queue (a too-slow consumer), fail fast: the
        connection is disconnected rather than silently dropping or
        blocking the caller — see plan §3.4.
        """
        if self._closed:
            return
        try:
            self._queue.put_nowait(envelope)
        except asyncio.QueueFull:
            logger.warning(
                "websocket.send_queue_overflow",
                connection_id=str(self.connection_id),
                user_id=str(self.user_id),
            )
            await self._on_disconnect_needed(self)

    async def _write_loop(self) -> None:
        try:
            while True:
                envelope = await self._queue.get()
                try:
                    await self.websocket.send_text(envelope.model_dump_json())
                except Exception:
                    logger.exception(
                        "websocket.write_failed",
                        connection_id=str(self.connection_id),
                    )
                    await self._on_disconnect_needed(self)
                    return
        except asyncio.CancelledError:
            pass

    async def close(self, *, already_disconnected: bool = False) -> None:
        """Idempotent teardown: cancel the writer task and close the
        socket. Safe to call from `on_disconnect_needed` itself, even
        though that callback runs *inside* the writer task on a write
        failure — a task can't await itself, so in that case the writer
        task (already about to return on its own) is left uncancelled
        and unawaited here.

        `already_disconnected=True` skips the socket close entirely —
        pass it when the caller already knows the transport is gone (a
        clean client-initiated disconnect: the ASGI server tears the
        connection down as soon as it delivers `websocket.disconnect`, so
        sending a `websocket.close` afterward isn't just redundant, it's
        invalid protocol state and uvicorn raises for it — this used to
        happen, and get silently swallowed by the `except Exception`
        below, on *every* ordinary client disconnect, not just races.
        """
        if self._closed:
            return
        self._closed = True
        if asyncio.current_task() is not self._writer_task:
            self._writer_task.cancel()
            try:
                await self._writer_task
            except asyncio.CancelledError:
                pass
        if already_disconnected:
            return
        try:
            await self.websocket.close()
        except Exception:
            logger.exception(
                "websocket.close_failed",
                connection_id=str(self.connection_id),
            )
