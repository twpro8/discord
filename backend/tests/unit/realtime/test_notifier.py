import asyncio
import json
from uuid import uuid4

from src.core.realtime.envelope import EventType
from src.core.realtime.notifier import LocalRealtimeNotifier
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
        # Never actually called: these tests only exercise the send path
        # (no `serve()` reader loop spawned), this just satisfies
        # ManagedWebSocket's structural type for `manager.connect(...)`.
        raise NotImplementedError


async def test_publish_to_a_users_pseudo_room_is_just_publish_to_room() -> None:
    # No dedicated "publish to user" method — user_room(user_id) is a room
    # like any other, reached the same way as chat:{chat_id} etc.
    manager = ConnectionManager()
    user_id = uuid4()
    ws = _FakeWebSocket()
    connection = await manager.connect(ws, user_id)
    await manager.join_room(connection, user_room(user_id))

    notifier = LocalRealtimeNotifier(manager)
    await notifier.publish_to_room(
        user_room(user_id), EventType.MESSAGE_CREATED, {"body": "hi"}
    )
    await asyncio.sleep(0)

    assert len(ws.sent) == 1
    decoded = json.loads(ws.sent[0])
    assert decoded["type"] == "message.created"
    assert decoded["payload"] == {"body": "hi"}
    assert decoded["room"] == user_room(user_id)

    await manager.disconnect(connection)


async def test_publish_to_room_only_reaches_members_of_that_room() -> None:
    manager = ConnectionManager()
    member_ws = _FakeWebSocket()
    non_member_ws = _FakeWebSocket()
    member = await manager.connect(member_ws, uuid4())
    non_member = await manager.connect(non_member_ws, uuid4())
    await manager.join_room(member, "chat:1")

    notifier = LocalRealtimeNotifier(manager)
    await notifier.publish_to_room("chat:1", EventType.MESSAGE_CREATED, {"a": 1})
    await asyncio.sleep(0)

    assert len(member_ws.sent) == 1
    assert non_member_ws.sent == []

    await manager.disconnect(member)
    await manager.disconnect(non_member)
