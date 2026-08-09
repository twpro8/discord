from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(StrEnum):
    """Wire-level event discriminator for realtime Envelopes.

    Values are the literal strings sent over the wire (not category
    names) so they match what the frontend's `RealtimeEvent` type already
    expects (e.g. MESSAGE_CREATED == "message.created") with no
    translation layer between the two.
    """

    MESSAGE_CREATED = "message.created"
    MESSAGE_UPDATED = "message.updated"
    MESSAGE_DELETED = "message.deleted"
    PRESENCE_UPDATE = "presence.update"
    TYPING_UPDATE = "typing.update"
    HEARTBEAT = "heartbeat"
    JOIN = "room.join"
    LEAVE = "room.leave"
    ACK = "ack"
    ERROR = "error"
    CALL_INVITE = "call.invite"
    CALL_ACCEPTED = "call.accepted"
    CALL_REJECTED = "call.rejected"
    CALL_CANCELLED = "call.cancelled"
    CALL_BUSY = "call.busy"
    CALL_TIMEOUT = "call.timeout"
    CALL_HANGUP = "call.hangup"
    CALL_OFFER = "call.offer"
    CALL_ANSWER = "call.answer"
    CALL_ICE_CANDIDATE = "call.ice_candidate"


class Envelope(BaseModel):
    """Shared message shape flowing over both WebSocket and Redis PubSub.

    `payload` stays a loose dict rather than a typed union: producers own
    their own payload shape (e.g. a ChatMessage dataclass via `asdict`),
    and this layer never needs to know it.
    """

    type: EventType
    payload: dict[str, Any]
    room: str | None = None
    event_id: UUID = Field(default_factory=uuid4)
    ts: datetime = Field(default_factory=lambda: datetime.now(UTC))
