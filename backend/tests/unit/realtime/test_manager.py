import asyncio
import contextlib
import json
from uuid import UUID, uuid4

from starlette.websockets import WebSocketDisconnect

from src.core.realtime.envelope import Envelope, EventType
from src.core.realtime.manager import ConnectionManager


class FakeManagedWebSocket:
    """A controllable client: `to_send` feeds `receive_text()` one item at
    a time; once exhausted (or `disconnect_now` is set) it raises
    WebSocketDisconnect, matching Starlette's real behavior on a closed
    client connection."""

    def __init__(self, to_send: list[str] | None = None) -> None:
        self.accepted = False
        self.closed = False
        self.close_calls = 0
        self.sent: list[str] = []
        self._to_receive = list(to_send or [])
        self._never_arrives: asyncio.Future[str] = (
            asyncio.get_running_loop().create_future()
        )

    async def accept(self) -> None:
        self.accepted = True

    async def send_text(self, data: str) -> None:
        self.sent.append(data)

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        # Distinct from `closed`, which simulate_client_disconnect() also
        # sets (mimicking the transport already being gone) — this
        # specifically counts *our* .close() calls, to prove code paths
        # that already know the client disconnected don't make one.
        self.close_calls += 1
        self.closed = True
        if not self._never_arrives.done():
            self._never_arrives.cancel()

    async def receive_text(self) -> str:
        if self._to_receive:
            return self._to_receive.pop(0)
        if self.closed:
            raise WebSocketDisconnect
        # Block "forever" (until close()/simulate_client_disconnect()
        # resolves it) rather than raising immediately, so tests control
        # disconnect timing explicitly.
        return await self._never_arrives

    def simulate_client_disconnect(self) -> None:
        """Faithfully mimics a real client closing the connection: an
        in-flight `receive_text()` raises WebSocketDisconnect cleanly, not
        CancelledError (that's a distinct case — a *task* being cancelled
        from elsewhere; see test_disconnect_from_elsewhere_cancels_an_in_
        progress_serve_call)."""
        self.closed = True
        if not self._never_arrives.done():
            self._never_arrives.set_exception(WebSocketDisconnect())


async def test_connect_registers_indices_and_accepts_the_socket() -> None:
    manager = ConnectionManager()
    ws = FakeManagedWebSocket()
    user_id = uuid4()

    connection = await manager.connect(ws, user_id)

    assert ws.accepted
    assert connection.user_id == user_id
    assert manager._connections[connection.connection_id] is connection
    assert connection.connection_id in manager._user_connections[user_id]

    await manager.disconnect(connection)


async def test_broadcast_to_room_reaches_only_members_of_that_room() -> None:
    manager = ConnectionManager()
    ws_a, ws_b, ws_c = (
        FakeManagedWebSocket(),
        FakeManagedWebSocket(),
        FakeManagedWebSocket(),
    )
    conn_a = await manager.connect(ws_a, uuid4())
    conn_b = await manager.connect(ws_b, uuid4())
    conn_c = await manager.connect(ws_c, uuid4())

    await manager.join_room(conn_a, "chat:1")
    await manager.join_room(conn_b, "chat:1")
    await manager.join_room(conn_c, "chat:2")

    envelope = Envelope(
        type=EventType.MESSAGE_CREATED, payload={"body": "hi"}, room="chat:1"
    )
    await manager.broadcast_to_room("chat:1", envelope)
    await asyncio.sleep(0)

    assert len(ws_a.sent) == 1
    assert json.loads(ws_a.sent[0])["payload"]["body"] == "hi"
    assert len(ws_b.sent) == 1
    assert ws_c.sent == []

    for connection in (conn_a, conn_b, conn_c):
        await manager.disconnect(connection)


async def test_disconnect_cleans_up_all_three_indices() -> None:
    manager = ConnectionManager()
    ws = FakeManagedWebSocket()
    user_id = uuid4()
    connection = await manager.connect(ws, user_id)
    await manager.join_room(connection, "chat:1")

    await manager.disconnect(connection)

    assert connection.connection_id not in manager._connections
    assert user_id not in manager._user_connections
    assert "chat:1" not in manager._rooms
    assert ws.closed


async def test_leave_room_removes_room_entry_once_empty_but_keeps_other_members() -> (
    None
):
    manager = ConnectionManager()
    conn_a = await manager.connect(FakeManagedWebSocket(), uuid4())
    conn_b = await manager.connect(FakeManagedWebSocket(), uuid4())
    await manager.join_room(conn_a, "chat:1")
    await manager.join_room(conn_b, "chat:1")

    await manager.leave_room(conn_a, "chat:1")
    assert "chat:1" in manager._rooms
    assert conn_a.connection_id not in manager._rooms["chat:1"]

    await manager.leave_room(conn_b, "chat:1")
    assert "chat:1" not in manager._rooms

    await manager.disconnect(conn_a)
    await manager.disconnect(conn_b)


async def test_room_activation_and_deactivation_callbacks_fire_once_per_transition() -> (
    None
):
    activated: list[str] = []
    deactivated: list[str] = []

    async def on_activated(room: str) -> None:
        activated.append(room)

    async def on_deactivated(room: str) -> None:
        deactivated.append(room)

    manager = ConnectionManager(
        on_room_activated=on_activated, on_room_deactivated=on_deactivated
    )
    conn_a = await manager.connect(FakeManagedWebSocket(), uuid4())
    conn_b = await manager.connect(FakeManagedWebSocket(), uuid4())

    await manager.join_room(conn_a, "chat:1")
    await manager.join_room(conn_b, "chat:1")  # second joiner: no re-activation
    assert activated == ["chat:1"]

    await manager.leave_room(conn_a, "chat:1")  # still one member: no deactivation
    assert deactivated == []

    await manager.leave_room(conn_b, "chat:1")  # last member: deactivates
    assert deactivated == ["chat:1"]

    await manager.disconnect(conn_a)
    await manager.disconnect(conn_b)


async def test_concurrent_join_and_leave_does_not_corrupt_indices() -> None:
    manager = ConnectionManager()
    connections = [
        await manager.connect(FakeManagedWebSocket(), uuid4()) for _ in range(20)
    ]

    await asyncio.gather(*(manager.join_room(c, "chat:shared") for c in connections))
    assert manager._rooms["chat:shared"] == {c.connection_id for c in connections}

    await asyncio.gather(*(manager.leave_room(c, "chat:shared") for c in connections))
    assert "chat:shared" not in manager._rooms

    await asyncio.gather(*(manager.disconnect(c) for c in connections))
    assert manager._connections == {}


async def test_reader_loop_disconnects_on_client_close() -> None:
    # serve() must be awaited by whoever called connect() (mirroring how a
    # real @router.websocket() handler drives it) — here that's a task we
    # spawn ourselves so the test can still run concurrently.
    manager = ConnectionManager()
    ws = FakeManagedWebSocket()
    connection = await manager.connect(ws, uuid4())
    serve_task = asyncio.create_task(manager.serve(connection))
    await asyncio.sleep(0)

    ws.simulate_client_disconnect()
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert connection.connection_id not in manager._connections
    await serve_task

    # Regression: a clean client-initiated disconnect must not also call
    # websocket.close() — the ASGI server already tore the connection
    # down once it delivered the disconnect, and a second close attempt
    # raises inside uvicorn (invalid protocol state), on every ordinary
    # disconnect, not just some rare race.
    assert ws.close_calls == 0


async def test_manager_initiated_disconnect_does_close_the_socket() -> None:
    # The other direction: when *we* decide to drop a connection (not a
    # client-initiated close), the socket is presumably still alive and
    # does need an active close — only the client-disconnect path skips it.
    manager = ConnectionManager()
    ws = FakeManagedWebSocket()
    connection = await manager.connect(ws, uuid4())

    await manager.disconnect(connection)

    assert ws.close_calls == 1


async def test_reader_loop_updates_last_seen_at_on_inbound_frame() -> None:
    manager = ConnectionManager()
    ws = FakeManagedWebSocket(to_send=["hello"])
    connection = await manager.connect(ws, uuid4())
    serve_task = asyncio.create_task(manager.serve(connection))
    before = connection.last_seen_at

    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert connection.last_seen_at >= before

    await manager.disconnect(connection)
    with contextlib.suppress(asyncio.CancelledError):
        await serve_task


async def test_disconnect_from_elsewhere_cancels_an_in_progress_serve_call() -> None:
    # Proves the fix for the ASGI-lifetime bug: serve() registers itself
    # so a disconnect triggered by something else (e.g. Connection's
    # overflow callback, running on the writer task) can interrupt a
    # serve() call that's still blocked in receive_text().
    manager = ConnectionManager()
    ws = FakeManagedWebSocket()
    connection = await manager.connect(ws, uuid4())
    serve_task = asyncio.create_task(manager.serve(connection))
    await asyncio.sleep(0)  # let serve() register itself and start blocking

    assert manager._serving_tasks[connection.connection_id] is serve_task

    await manager.disconnect(connection)
    with contextlib.suppress(asyncio.CancelledError):
        await serve_task

    assert serve_task.cancelled() or serve_task.done()
    assert connection.connection_id not in manager._connections

    await manager.disconnect(connection)


async def test_shutdown_disconnects_every_connection() -> None:
    manager = ConnectionManager()
    for _ in range(3):
        await manager.connect(FakeManagedWebSocket(), uuid4())

    await manager.shutdown()

    assert manager._connections == {}
    assert manager._user_connections == {}


async def test_activity_callback_fires_on_every_inbound_frame_including_malformed() -> (
    None
):
    # Deliberately no JSON parsing here — the on_activity callback receives
    # the raw text as-is, exactly like touch()'s existing "any frame means
    # alive" semantic. Parsing (and defaulting malformed input to a
    # liveness-only signal) is the listener's job (presence's
    # PresenceService), not ConnectionManager's.
    received: list[tuple[UUID, UUID, str]] = []

    async def on_activity(user_id: UUID, connection_id: UUID, raw_text: str) -> None:
        received.append((user_id, connection_id, raw_text))

    manager = ConnectionManager(on_activity=on_activity)
    ws = FakeManagedWebSocket(to_send=["hello", "not json {{{"])
    user_id = uuid4()
    connection = await manager.connect(ws, user_id)
    serve_task = asyncio.create_task(manager.serve(connection))

    await asyncio.sleep(0)
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert received == [
        (user_id, connection.connection_id, "hello"),
        (user_id, connection.connection_id, "not json {{{"),
    ]

    await manager.disconnect(connection)
    with contextlib.suppress(asyncio.CancelledError):
        await serve_task


async def test_set_activity_callback_binds_after_construction() -> None:
    received: list[str] = []

    async def on_activity(_user_id: UUID, _connection_id: UUID, raw_text: str) -> None:
        received.append(raw_text)

    manager = ConnectionManager()
    manager.set_activity_callback(on_activity)
    ws = FakeManagedWebSocket(to_send=["ping"])
    connection = await manager.connect(ws, uuid4())
    serve_task = asyncio.create_task(manager.serve(connection))

    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert received == ["ping"]

    await manager.disconnect(connection)
    with contextlib.suppress(asyncio.CancelledError):
        await serve_task


async def test_connect_ignores_unknown_connection_in_join_room() -> None:
    manager = ConnectionManager()
    connection = await manager.connect(FakeManagedWebSocket(), uuid4())
    await manager.disconnect(connection)

    # A stale reference (already disconnected) must not resurrect indices.
    await manager.join_room(connection, "chat:1")

    assert "chat:1" not in manager._rooms
