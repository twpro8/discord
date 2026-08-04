from __future__ import annotations

import asyncio
from typing import Any
from uuid import uuid4

from fakeredis.aioredis import FakeRedis

from src.core.realtime.membership import DistributedRoomMembershipUpdater
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.realtime.rooms import user_room
from src.core.websocket.manager import ConnectionManager


class _FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def accept(self) -> None:
        pass

    async def send_text(self, data: str) -> None:
        self.sent.append(data)

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        pass

    async def receive_text(self) -> str:
        future: asyncio.Future[str] = asyncio.get_running_loop().create_future()
        return await future


def _wire(redis: Any) -> tuple[ConnectionManager, RedisSubscriptionManager]:
    connection_manager = ConnectionManager()
    subscription_manager = RedisSubscriptionManager(
        redis, connection_manager, poll_timeout_seconds=0.05
    )
    connection_manager.set_room_transition_callbacks(
        on_room_activated=subscription_manager.on_room_activated,
        on_room_deactivated=subscription_manager.on_room_deactivated,
    )
    return connection_manager, subscription_manager


async def test_join_reaches_a_connection_open_on_a_different_instance() -> None:
    """The gap this whole class exists to close: a request handled on
    instance 1 grants room access to a user whose only open connection is
    on instance 2."""
    redis = FakeRedis(decode_responses=True)
    cm1, sub1 = _wire(redis)
    cm2, sub2 = _wire(redis)
    sub1.start()
    sub2.start()

    user_id = uuid4()
    ws = _FakeWebSocket()
    connection = await cm2.connect(ws, user_id)
    await cm2.join_room(connection, user_room(user_id))  # auto-join, as ws.py does
    await asyncio.sleep(0.2)  # let the subscribe reach Redis

    updater = DistributedRoomMembershipUpdater(sub1)
    await updater.join_user_to_room(user_id, "chat:1")
    await asyncio.sleep(0.2)  # let the control envelope round-trip back

    assert "chat:1" in cm2._rooms
    assert connection.connection_id in cm2._rooms["chat:1"]
    assert "chat:1" not in cm1._rooms  # cm1 has no local connections at all

    await sub1.stop()
    await sub2.stop()


async def test_join_also_reaches_a_connection_on_the_same_instance() -> None:
    """No local-direct fast path — this instance's own connections learn
    about the join the same way any other instance's would, via Redis."""
    redis = FakeRedis(decode_responses=True)
    cm1, sub1 = _wire(redis)
    sub1.start()

    user_id = uuid4()
    ws = _FakeWebSocket()
    connection = await cm1.connect(ws, user_id)
    await cm1.join_room(connection, user_room(user_id))
    await asyncio.sleep(0.2)

    updater = DistributedRoomMembershipUpdater(sub1)
    await updater.join_user_to_room(user_id, "chat:1")
    await asyncio.sleep(0.2)

    assert connection.connection_id in cm1._rooms.get("chat:1", set())

    await sub1.stop()


async def test_leave_removes_the_connection_from_the_room_on_another_instance() -> None:
    redis = FakeRedis(decode_responses=True)
    _cm1, sub1 = _wire(redis)
    cm2, sub2 = _wire(redis)
    sub1.start()
    sub2.start()

    user_id = uuid4()
    connection = await cm2.connect(_FakeWebSocket(), user_id)
    await cm2.join_room(connection, user_room(user_id))
    await cm2.join_room(connection, "chat:1")
    await asyncio.sleep(0.2)

    updater = DistributedRoomMembershipUpdater(sub1)
    await updater.leave_user_from_room(user_id, "chat:1")
    await asyncio.sleep(0.2)

    assert "chat:1" not in cm2._rooms

    await sub1.stop()
    await sub2.stop()


async def test_join_control_envelope_is_never_delivered_to_the_socket() -> None:
    """The join signal is server-internal — it must not show up as a
    message the client receives, unlike a real EventType.MESSAGE_CREATED
    publish to the same room."""
    redis = FakeRedis(decode_responses=True)
    cm1, sub1 = _wire(redis)
    sub1.start()

    user_id = uuid4()
    ws = _FakeWebSocket()
    connection = await cm1.connect(ws, user_id)
    await cm1.join_room(connection, user_room(user_id))
    await asyncio.sleep(0.2)

    updater = DistributedRoomMembershipUpdater(sub1)
    await updater.join_user_to_room(user_id, "chat:1")
    await asyncio.sleep(0.2)

    assert ws.sent == []

    await sub1.stop()


async def test_join_for_a_user_with_no_connection_anywhere_is_a_harmless_noop() -> None:
    redis = FakeRedis(decode_responses=True)
    _cm1, sub1 = _wire(redis)
    sub1.start()

    updater = DistributedRoomMembershipUpdater(sub1)
    await updater.join_user_to_room(uuid4(), "chat:1")
    await asyncio.sleep(0.1)  # nothing to assert beyond "this doesn't raise"

    await sub1.stop()
