import asyncio
import json
from uuid import uuid4

from src.core.realtime.envelope import Envelope, EventType
from src.core.realtime.connection import Connection


class FakeWebSocket:
    def __init__(self, block_sends: bool = False) -> None:
        self.sent: list[str] = []
        self.closed = False
        self._block_sends = block_sends
        self._release = asyncio.Event()

    async def send_text(self, data: str) -> None:
        if self._block_sends:
            await self._release.wait()
        self.sent.append(data)

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        self.closed = True

    def release(self) -> None:
        self._release.set()


class FailingWebSocket:
    async def send_text(self, data: str) -> None:
        raise ConnectionResetError

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        pass


async def test_send_delivers_envelope_via_writer_task() -> None:
    ws = FakeWebSocket()
    connection = Connection(
        ws, uuid4(), queue_maxsize=8, on_disconnect_needed=_noop_disconnect
    )

    await connection.send(Envelope(type=EventType.HEARTBEAT, payload={"n": 1}))
    await asyncio.sleep(0)

    assert len(ws.sent) == 1
    assert json.loads(ws.sent[0])["payload"] == {"n": 1}

    await connection.close()


async def test_sends_preserve_order() -> None:
    ws = FakeWebSocket()
    connection = Connection(
        ws, uuid4(), queue_maxsize=8, on_disconnect_needed=_noop_disconnect
    )

    for i in range(5):
        await connection.send(Envelope(type=EventType.HEARTBEAT, payload={"n": i}))
    await asyncio.sleep(0)

    assert [json.loads(m)["payload"]["n"] for m in ws.sent] == [0, 1, 2, 3, 4]

    await connection.close()


async def test_overflow_triggers_disconnect_callback_instead_of_blocking_or_dropping() -> (
    None
):
    ws = FakeWebSocket(block_sends=True)
    disconnected: list[Connection] = []

    async def on_disconnect_needed(connection: Connection) -> None:
        disconnected.append(connection)

    connection = Connection(
        ws, uuid4(), queue_maxsize=1, on_disconnect_needed=on_disconnect_needed
    )
    heartbeat = Envelope(type=EventType.HEARTBEAT, payload={})

    await connection.send(heartbeat)
    await asyncio.sleep(0)  # let the writer dequeue into the blocked send_text
    await connection.send(heartbeat)  # refills the now-empty queue (maxsize=1)
    await connection.send(heartbeat)  # queue full -> overflow, not a block/drop

    assert disconnected == [connection]

    ws.release()
    await connection.close()


async def test_write_failure_triggers_disconnect_callback() -> None:
    # A realistic ConnectionManager callback calls connection.close() right
    # back — this must not deadlock even though the callback runs inside
    # the writer task itself (a task can't await itself; see Connection.close).
    disconnected: list[Connection] = []

    async def on_disconnect_needed(connection: Connection) -> None:
        disconnected.append(connection)
        await connection.close()

    connection = Connection(
        FailingWebSocket(),
        uuid4(),
        queue_maxsize=8,
        on_disconnect_needed=on_disconnect_needed,
    )

    await connection.send(Envelope(type=EventType.HEARTBEAT, payload={}))
    await asyncio.sleep(0)

    assert disconnected == [connection]


async def test_close_cancels_writer_task_and_closes_socket() -> None:
    ws = FakeWebSocket()
    connection = Connection(
        ws, uuid4(), queue_maxsize=8, on_disconnect_needed=_noop_disconnect
    )

    await connection.close()

    assert ws.closed
    assert connection._writer_task.cancelled() or connection._writer_task.done()


async def test_close_with_already_disconnected_skips_the_socket_close_call() -> None:
    # Regression: calling websocket.close() after the ASGI server already
    # tore the connection down (a clean client-initiated disconnect)
    # raises inside uvicorn — close() must not attempt it in that case.
    ws = FakeWebSocket()
    connection = Connection(
        ws, uuid4(), queue_maxsize=8, on_disconnect_needed=_noop_disconnect
    )

    await connection.close(already_disconnected=True)

    assert ws.closed is False
    assert connection._writer_task.cancelled() or connection._writer_task.done()


async def test_send_after_close_is_a_noop() -> None:
    ws = FakeWebSocket()
    connection = Connection(
        ws, uuid4(), queue_maxsize=8, on_disconnect_needed=_noop_disconnect
    )
    await connection.close()

    await connection.send(Envelope(type=EventType.HEARTBEAT, payload={}))
    await asyncio.sleep(0)

    assert ws.sent == []


async def test_connection_ids_are_unique() -> None:
    ws = FakeWebSocket()
    user_id = uuid4()
    first = Connection(
        ws, user_id, queue_maxsize=8, on_disconnect_needed=_noop_disconnect
    )
    second = Connection(
        ws, user_id, queue_maxsize=8, on_disconnect_needed=_noop_disconnect
    )

    assert first.connection_id != second.connection_id
    assert first.user_id == second.user_id == user_id

    await first.close()
    await second.close()


async def _noop_disconnect(_connection: Connection) -> None:
    pass
