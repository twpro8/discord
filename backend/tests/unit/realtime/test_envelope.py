import json

from src.core.realtime.envelope import Envelope, EventType


def test_message_created_envelope_matches_frontend_contract() -> None:
    envelope = Envelope(
        type=EventType.MESSAGE_CREATED,
        payload={"chat_id": "c1", "body": "hi"},
        room="chat:c1",
    )

    decoded = json.loads(envelope.model_dump_json())

    assert decoded["type"] == "message.created"
    assert decoded["payload"] == {"chat_id": "c1", "body": "hi"}


def test_extra_envelope_fields_are_additive_not_replacing_payload() -> None:
    envelope = Envelope(
        type=EventType.MESSAGE_CREATED, payload={"a": 1}, room="chat:c1"
    )

    decoded = json.loads(envelope.model_dump_json())

    assert set(decoded) >= {"type", "payload", "room", "event_id", "ts"}
    assert decoded["payload"] == {"a": 1}


def test_room_defaults_to_none_for_non_room_scoped_events() -> None:
    envelope = Envelope(type=EventType.HEARTBEAT, payload={})

    assert envelope.room is None


def test_event_id_is_unique_per_envelope() -> None:
    first = Envelope(type=EventType.ACK, payload={})
    second = Envelope(type=EventType.ACK, payload={})

    assert first.event_id != second.event_id
