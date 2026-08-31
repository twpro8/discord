from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from fakeredis.aioredis import FakeRedis

from src.core.realtime.envelope import Envelope, EventType
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.realtime.manager import ConnectionManager


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


def _wire(
    redis: Any, *, poll_timeout_seconds: float = 0.05, **kwargs: Any
) -> tuple[ConnectionManager, RedisSubscriptionManager]:
    connection_manager = ConnectionManager()
    subscription_manager = RedisSubscriptionManager(
        redis, connection_manager, poll_timeout_seconds=poll_timeout_seconds, **kwargs
    )
    connection_manager.set_room_transition_callbacks(
        on_room_activated=subscription_manager.on_room_activated,
        on_room_deactivated=subscription_manager.on_room_deactivated,
    )
    return connection_manager, subscription_manager


async def test_publish_reaches_a_locally_connected_socket_on_another_instance() -> None:
    """Two ConnectionManager/RedisSubscriptionManager pairs sharing one
    Redis, simulating two app processes."""
    redis = FakeRedis(decode_responses=True)
    _cm1, sub1 = _wire(redis)
    cm2, sub2 = _wire(redis)
    sub1.start()
    sub2.start()

    ws = _FakeWebSocket()
    connection = await cm2.connect(ws, uuid4())
    await cm2.join_room(connection, "chat:1")
    await asyncio.sleep(0.2)  # let the subscribe request propagate to Redis

    await sub1.publish(
        "chat:1", Envelope(type=EventType.MESSAGE_CREATED, payload={"body": "hi"})
    )
    await asyncio.sleep(0.2)  # let the message propagate back

    assert len(ws.sent) == 1
    assert json.loads(ws.sent[0])["payload"] == {"body": "hi"}

    await sub1.stop()
    await sub2.stop()


async def test_publish_does_not_reach_a_socket_that_never_joined_the_room() -> None:
    redis = FakeRedis(decode_responses=True)
    _cm1, sub1 = _wire(redis)
    cm2, sub2 = _wire(redis)
    sub1.start()
    sub2.start()

    ws = _FakeWebSocket()
    connection = await cm2.connect(ws, uuid4())
    await cm2.join_room(connection, "chat:other")
    await asyncio.sleep(0.2)

    await sub1.publish(
        "chat:1", Envelope(type=EventType.MESSAGE_CREATED, payload={"body": "hi"})
    )
    await asyncio.sleep(0.2)

    assert ws.sent == []

    await sub1.stop()
    await sub2.stop()


async def test_leaving_a_room_stops_further_delivery() -> None:
    redis = FakeRedis(decode_responses=True)
    _cm1, sub1 = _wire(redis)
    cm2, sub2 = _wire(redis)
    sub1.start()
    sub2.start()

    ws = _FakeWebSocket()
    connection = await cm2.connect(ws, uuid4())
    await cm2.join_room(connection, "chat:1")
    await asyncio.sleep(0.2)

    await cm2.leave_room(connection, "chat:1")
    await asyncio.sleep(0.2)

    await sub1.publish(
        "chat:1", Envelope(type=EventType.MESSAGE_CREATED, payload={"body": "hi"})
    )
    await asyncio.sleep(0.2)

    assert ws.sent == []

    await sub1.stop()
    await sub2.stop()


class _FlakyPubSub:
    def __init__(self, parent: _FlakyRedis) -> None:
        self._parent = parent

    async def subscribe(self, *channels: str) -> None:
        self._parent.subscribe_calls.append(channels)
        self._parent.maybe_fail()

    async def unsubscribe(self, *channels: str) -> None:
        pass

    async def get_message(
        self, *, ignore_subscribe_messages: bool, timeout: float
    ) -> Mapping[str, Any] | None:
        # Real redis-py genuinely awaits up to `timeout` — mirror that so
        # this doesn't busy-loop with no yield point (which would starve
        # task cancellation from ever landing).
        await asyncio.sleep(timeout)
        return None

    async def aclose(self) -> None:
        pass


class _FlakyRedis:
    """Fails the first `fail_times` subscribe attempts with a connection
    error, then behaves — proves backoff + full re-subscribe on
    reconnect without needing a real flaky Redis."""

    def __init__(self, fail_times: int) -> None:
        self._fail_times = fail_times
        self._attempts = 0
        self.subscribe_calls: list[tuple[str, ...]] = []

    def maybe_fail(self) -> None:
        if self._attempts < self._fail_times:
            self._attempts += 1
            raise ConnectionError("simulated connection failure")

    def pubsub(self) -> _FlakyPubSub:
        return _FlakyPubSub(self)

    async def publish(self, channel: str, message: str) -> int:
        return 0


async def test_reconnects_with_backoff_and_resubscribes_after_connection_loss() -> None:
    redis = _FlakyRedis(fail_times=2)
    connection_manager, subscription_manager = _wire(
        redis,
        poll_timeout_seconds=0.05,
        backoff_base_seconds=0.01,
        backoff_max_seconds=0.05,
        backoff_jitter=1.0,  # no randomness: deterministic delay in tests
    )
    ws = _FakeWebSocket()
    connection = await connection_manager.connect(ws, uuid4())
    await connection_manager.join_room(connection, "chat:1")

    subscription_manager.start()
    await asyncio.sleep(0.3)  # long enough to fail twice, back off, and recover

    # 3 attempts total: 2 failures + 1 success, each re-subscribing to the
    # full desired set (just "chat:1" here) since actual state was wiped
    # by each disconnect.
    assert redis.subscribe_calls == [("chat:1",), ("chat:1",), ("chat:1",)]
    assert subscription_manager._actual_subscribed == {"chat:1"}

    await subscription_manager.stop()
