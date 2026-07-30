from collections.abc import AsyncIterator
from typing import Protocol

from redis.asyncio import Redis


class PubSubTransport(Protocol):
    """Generic publish/subscribe transport over raw string topics and
    payloads.

    This is NOT the same thing as core.event_bus.EventBus:
      - EventBus carries typed DomainEvent objects between MODULES, for
        consistency-relevant, relatively rare occurrences.
      - PubSubTransport carries opaque str payloads between PROCESSES (app
        instances behind a load balancer) for high-frequency realtime
        fan-out to open WebSocket connections.
    Using EventBus for realtime WS fan-out (or vice versa) is a sign the
    two concepts have been conflated.
    """

    async def publish(self, topic: str, payload: str) -> None: ...

    def subscribe(self, topic: str) -> AsyncIterator[str]: ...


class RedisPubSubTransport:
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def publish(self, topic: str, payload: str) -> None:
        await self._client.publish(topic, payload)

    async def subscribe(self, topic: str) -> AsyncIterator[str]:
        pubsub = self._client.pubsub()
        await pubsub.subscribe(topic)
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                yield message["data"]
        finally:
            await pubsub.unsubscribe(topic)
            await pubsub.aclose()  # type: ignore[no-untyped-call]
