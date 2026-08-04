import asyncio
import contextlib
import random
from collections.abc import Mapping
from typing import Any, Protocol
from uuid import UUID

from pydantic import ValidationError

from src.core.logging import get_logger
from src.core.realtime.envelope import Envelope, EventType
from src.core.websocket.manager import ConnectionManager

logger = get_logger(__name__)


class RedisPubSubLike(Protocol):
    """What RedisSubscriptionManager needs from a single subscription
    connection — matches redis.asyncio.client.PubSub's shape structurally,
    so a real client needs no adapter and a test fake needs no more than
    this."""

    async def subscribe(self, *channels: str) -> None: ...

    async def unsubscribe(self, *channels: str) -> None: ...

    async def get_message(
        self, *, ignore_subscribe_messages: bool, timeout: float
    ) -> Mapping[str, Any] | None: ...

    async def aclose(self) -> None: ...


class RedisLike(Protocol):
    """What RedisSubscriptionManager needs from the top-level client —
    matches redis.asyncio.Redis's shape structurally."""

    def pubsub(self) -> RedisPubSubLike: ...

    async def publish(self, channel: str, message: str) -> int: ...


_SubscriptionRequest = tuple[str, str]  # ("subscribe" | "unsubscribe", room)


class RedisSubscriptionManager:
    """Cross-instance fan-out: subscribes to Redis channels for rooms that
    have at least one *local* subscriber (learned via ConnectionManager's
    on_room_activated/on_room_deactivated hooks), and delivers inbound
    messages to this instance's ConnectionManager.

    A single background task owns the one PubSub connection object for
    this instance's entire lifetime — no other coroutine may call
    subscribe/unsubscribe/get_message on it directly (redis-py's asyncio
    PubSub isn't safe for concurrent use from multiple coroutines).
    join_room/leave_room-triggered requests are handed to that task via a
    queue instead, processed in the order they were generated — this is
    what keeps a room's subscribe/unsubscribe calls correctly ordered
    even under concurrent local join/leave churn, without needing a lock
    (see ConnectionManager.RoomTransitionCallback's docstring).

    Desired subscription state (self._desired_rooms) is tracked
    separately from actual Redis subscription state
    (self._actual_subscribed): on a connection loss, only the desired set
    survives, and reconnecting re-subscribes to all of it — a request
    queue alone wouldn't do this, since requests already drained before
    the disconnect aren't replayed.

    Deliberately Redis Pub/Sub, not Streams: no persistence, no
    at-least-once delivery, no catch-up on reconnect — a message
    published while this instance is disconnected is simply missed for
    any locally-connected sockets during that window. Acceptable
    (temporary) tradeoff for events with a REST catch-up path (chat
    messages can be re-fetched via list_chat_messages); not for ones
    without (future presence/typing).
    """

    def __init__(
        self,
        redis: RedisLike,
        connection_manager: ConnectionManager,
        *,
        backoff_base_seconds: float = 0.5,
        backoff_max_seconds: float = 30.0,
        backoff_jitter: float = 0.5,
        poll_timeout_seconds: float = 0.5,
    ) -> None:
        self._redis = redis
        self._connection_manager = connection_manager
        self._backoff_base = backoff_base_seconds
        self._backoff_max = backoff_max_seconds
        self._backoff_jitter = backoff_jitter
        self._poll_timeout = poll_timeout_seconds

        self._desired_rooms: set[str] = set()
        self._actual_subscribed: set[str] = set()
        self._pubsub: RedisPubSubLike | None = None
        self._requests: asyncio.Queue[_SubscriptionRequest] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None
        self._stopped = True
        self._attempt = 0

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
        if self._pubsub is not None:
            await self._pubsub.aclose()
            self._pubsub = None

    async def on_room_activated(self, room: str) -> None:
        """ConnectionManager RoomTransitionCallback: room gained its first
        local subscriber."""
        self._desired_rooms.add(room)
        await self._requests.put(("subscribe", room))

    async def on_room_deactivated(self, room: str) -> None:
        """ConnectionManager RoomTransitionCallback: room lost its last
        local subscriber."""
        self._desired_rooms.discard(room)
        await self._requests.put(("unsubscribe", room))

    async def publish(self, room: str, envelope: Envelope) -> None:
        """Always publishes to Redis regardless of local subscriber count
        for `room` — other instances may have local subscribers even if
        this one doesn't."""
        await self._redis.publish(room, envelope.model_dump_json())

    async def _run(self) -> None:
        while not self._stopped:
            try:
                await self._ensure_connected()
                await self._pump()
            except asyncio.CancelledError:
                raise
            except Exception as error:
                logger.warning("redis_subscription.connection_lost", error=str(error))
                self._pubsub = None
                self._actual_subscribed = set()
                await self._backoff_sleep()

    async def _pump(self) -> None:
        assert self._pubsub is not None
        # A pending get_message() call is kept across loop iterations
        # rather than being cancelled whenever a request arrives first —
        # cancelling it mid-flight risks corrupting the pubsub
        # connection's protocol state if cancellation lands mid-read.
        # Only ever cancel the always-safe-to-cancel queue.get() side.
        message_task: asyncio.Task[Mapping[str, Any] | None] | None = None
        try:
            while not self._stopped:
                await self._drain_requests()
                if not self._actual_subscribed:
                    # redis-py's PubSub.get_message() errors with zero
                    # active subscriptions (nothing to read) — the common
                    # steady state whenever no local connection has
                    # joined any room yet. Block for the next request
                    # instead of polling into that error.
                    if message_task is not None:
                        message_task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await message_task
                        message_task = None
                    action, room = await self._requests.get()
                    await self._apply_request(action, room)
                    continue

                if message_task is None:
                    message_task = asyncio.ensure_future(
                        self._pubsub.get_message(
                            ignore_subscribe_messages=True,
                            timeout=self._poll_timeout,
                        )
                    )
                request_task: asyncio.Task[_SubscriptionRequest] = (
                    asyncio.ensure_future(self._requests.get())
                )
                # Waiting on both concurrently (rather than draining
                # requests only *between* get_message() calls) is what
                # closes the race: without it, a room that becomes
                # desired while a get_message() call is already in
                # flight wouldn't get subscribed until that call returns
                # (up to poll_timeout_seconds later) — a real message
                # published to it in that window would simply be missed,
                # not just during a genuine disconnect (which is already
                # an accepted tradeoff) but during ordinary operation.
                done, _ = await asyncio.wait(
                    {message_task, request_task}, return_when=asyncio.FIRST_COMPLETED
                )

                if request_task in done:
                    action, room = request_task.result()
                    await self._apply_request(action, room)
                else:
                    request_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await request_task

                if message_task in done:
                    message = message_task.result()
                    message_task = None
                    if message is not None:
                        await self._handle_message(message)
        finally:
            if message_task is not None:
                message_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await message_task

    async def _ensure_connected(self) -> None:
        if self._pubsub is not None:
            return
        pubsub = self._redis.pubsub()
        if self._desired_rooms:
            await pubsub.subscribe(*self._desired_rooms)
        self._pubsub = pubsub
        self._actual_subscribed = set(self._desired_rooms)
        self._attempt = 0
        logger.info("redis_subscription.connected", room_count=len(self._desired_rooms))

    async def _drain_requests(self) -> None:
        while True:
            try:
                action, room = self._requests.get_nowait()
            except asyncio.QueueEmpty:
                return
            await self._apply_request(action, room)

    async def _apply_request(self, action: str, room: str) -> None:
        # Idempotency guards: a request queued before `start()` (or
        # already covered by _ensure_connected's bulk re-subscribe after
        # a reconnect) would otherwise issue a redundant, if harmless,
        # duplicate Redis call once drained.
        assert self._pubsub is not None
        if action == "subscribe":
            if room in self._actual_subscribed:
                return
            await self._pubsub.subscribe(room)
            self._actual_subscribed.add(room)
        else:
            if room not in self._actual_subscribed:
                return
            await self._pubsub.unsubscribe(room)
            self._actual_subscribed.discard(room)

    async def _handle_message(self, message: Mapping[str, Any]) -> None:
        channel = message.get("channel")
        data = message.get("data")
        if not isinstance(channel, str) or not isinstance(data, str):
            return
        try:
            envelope = Envelope.model_validate_json(data)
        except ValidationError:
            logger.warning("redis_subscription.invalid_envelope", room=channel)
            return

        if envelope.type in (EventType.JOIN, EventType.LEAVE):
            # Server-internal control-plane signal (see
            # core.realtime.membership.DistributedRoomMembershipUpdater),
            # never a client-facing message — applied locally, not
            # forwarded to any socket.
            await self._apply_room_membership_control(envelope)
            return

        await self._connection_manager.broadcast_to_room(channel, envelope)

    async def _apply_room_membership_control(self, envelope: Envelope) -> None:
        user_id_raw = envelope.payload.get("user_id")
        room = envelope.payload.get("room")
        if not isinstance(user_id_raw, str) or not isinstance(room, str):
            logger.warning(
                "redis_subscription.invalid_room_control", payload=envelope.payload
            )
            return
        try:
            user_id = UUID(user_id_raw)
        except ValueError:
            logger.warning(
                "redis_subscription.invalid_room_control", payload=envelope.payload
            )
            return

        if envelope.type == EventType.JOIN:
            await self._connection_manager.join_user_to_room(user_id, room)
        else:
            await self._connection_manager.leave_user_from_room(user_id, room)

    async def _backoff_sleep(self) -> None:
        delay = min(self._backoff_base * (2**self._attempt), self._backoff_max)
        delay *= self._backoff_jitter + random.random() * (1 - self._backoff_jitter)
        self._attempt += 1
        logger.info(
            "redis_subscription.reconnecting",
            delay_seconds=round(delay, 2),
            attempt=self._attempt,
        )
        await asyncio.sleep(delay)
