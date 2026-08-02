"""Illustrative — this is what modules/messages/infrastructure/websocket/
redis_subscriber.py would look like once `messages` grows a WebSocket
gateway. Not wired into anything; kept here as a concrete example of the
core.realtime -> module.infrastructure -> module.transport split.

    from src.core.realtime import PubSubTransport

    class ChannelRedisSubscriber:
        '''Knows the messages-module-specific topic convention
        ("channel:{channel_id}") and payload shape. This vocabulary is
        exactly why this class lives in modules/messages, not core/ —
        core.realtime doesn't know what a "channel" is.'''

        def __init__(self, transport: PubSubTransport) -> None:
            self._transport = transport

        async def publish_message_sent(self, channel_id: str, message_dto: "MessageDTO") -> None:
            await self._transport.publish(
                topic=f"channel:{channel_id}",
                payload=message_dto_to_json(message_dto),
            )

        def subscribe_to_channel(self, channel_id: str):
            return self._transport.subscribe(topic=f"channel:{channel_id}")

And transport/websocket/ws_gateway.py would own the actual FastAPI
WebSocket connections and pump events from subscribe_to_channel() into
whichever sockets are currently listening for that channel_id — that
bookkeeping (which connection wants which channel) is presentation-layer
state, not infrastructure.

Where the RedisSubscriber gets constructed and wired to a WS route is
decided in modules/messages/module.py, the same way UserUnitOfWorkImpl is
wired in modules/users/composition.py today.
"""
