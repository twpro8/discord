import json
from uuid import UUID, uuid4

from src.core.realtime.envelope import EventType
from src.core.realtime.rooms import chat_room
from src.modules.typing.application.typing_service import TypingService
from tests.unit.typing.fakes import FakeRealtimeNotifier


def _make_service(
    notifier: FakeRealtimeNotifier,
    *,
    in_room: bool = True,
    raise_on_room_check: bool = False,
    room_check_calls: list[tuple[UUID, str]] | None = None,
) -> TypingService:
    def is_connection_in_room(connection_id: UUID, room: str) -> bool:
        if room_check_calls is not None:
            room_check_calls.append((connection_id, room))
        if raise_on_room_check:
            raise RuntimeError("boom")
        return in_room

    return TypingService(is_connection_in_room, notifier)


async def test_on_activity_publishes_to_chat_room_when_connection_is_a_member() -> None:
    notifier = FakeRealtimeNotifier()
    service = _make_service(notifier, in_room=True)
    user_id, conn_id, chat_id = uuid4(), uuid4(), uuid4()

    await service.on_activity(
        user_id,
        conn_id,
        json.dumps({"type": "typing", "chat_id": str(chat_id), "is_typing": True}),
    )

    assert notifier.published == [
        (
            chat_room(chat_id),
            EventType.TYPING_UPDATE,
            {"chat_id": str(chat_id), "user_id": str(user_id), "is_typing": True},
        )
    ]


async def test_on_activity_drops_frame_when_connection_not_in_room() -> None:
    notifier = FakeRealtimeNotifier()
    service = _make_service(notifier, in_room=False)
    user_id, conn_id, chat_id = uuid4(), uuid4(), uuid4()

    await service.on_activity(
        user_id,
        conn_id,
        json.dumps({"type": "typing", "chat_id": str(chat_id), "is_typing": True}),
    )

    assert notifier.published == []


async def test_on_activity_ignores_non_typing_frames() -> None:
    notifier = FakeRealtimeNotifier()
    room_check_calls: list[tuple[UUID, str]] = []
    service = _make_service(notifier, room_check_calls=room_check_calls)
    user_id, conn_id = uuid4(), uuid4()

    await service.on_activity(
        user_id, conn_id, json.dumps({"type": "heartbeat", "idle": True})
    )

    assert notifier.published == []
    assert room_check_calls == []


async def test_on_activity_ignores_malformed_json() -> None:
    notifier = FakeRealtimeNotifier()
    service = _make_service(notifier)
    user_id, conn_id = uuid4(), uuid4()

    await service.on_activity(user_id, conn_id, "not json at all {{{")

    assert notifier.published == []


async def test_on_activity_ignores_frame_with_invalid_chat_id() -> None:
    notifier = FakeRealtimeNotifier()
    service = _make_service(notifier)
    user_id, conn_id = uuid4(), uuid4()

    await service.on_activity(
        user_id,
        conn_id,
        json.dumps({"type": "typing", "chat_id": "not-a-uuid", "is_typing": True}),
    )

    assert notifier.published == []


async def test_on_activity_defaults_missing_is_typing_to_false() -> None:
    notifier = FakeRealtimeNotifier()
    service = _make_service(notifier, in_room=True)
    user_id, conn_id, chat_id = uuid4(), uuid4(), uuid4()

    await service.on_activity(
        user_id, conn_id, json.dumps({"type": "typing", "chat_id": str(chat_id)})
    )

    assert notifier.published == [
        (
            chat_room(chat_id),
            EventType.TYPING_UPDATE,
            {"chat_id": str(chat_id), "user_id": str(user_id), "is_typing": False},
        )
    ]


async def test_notifier_failure_does_not_propagate() -> None:
    notifier = FakeRealtimeNotifier()
    chat_id = uuid4()
    notifier.raise_for_rooms = {chat_room(chat_id)}
    service = _make_service(notifier, in_room=True)
    user_id, conn_id = uuid4(), uuid4()

    await service.on_activity(
        user_id,
        conn_id,
        json.dumps({"type": "typing", "chat_id": str(chat_id), "is_typing": True}),
    )  # must not raise


async def test_room_check_raising_does_not_propagate() -> None:
    notifier = FakeRealtimeNotifier()
    service = _make_service(notifier, raise_on_room_check=True)
    user_id, conn_id, chat_id = uuid4(), uuid4(), uuid4()

    await service.on_activity(
        user_id,
        conn_id,
        json.dumps({"type": "typing", "chat_id": str(chat_id), "is_typing": True}),
    )  # must not raise

    assert notifier.published == []
