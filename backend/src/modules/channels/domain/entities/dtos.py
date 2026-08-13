from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.enums import ChannelType
from src.shared.domain.unset import UNSET, Unsettable


@dataclass(frozen=True, kw_only=True)
class ChannelCreate:
    server_id: UUID
    name: str
    type: ChannelType = ChannelType.text
    topic: str | None = None
    position: int = 0
    is_private: bool = False


@dataclass(frozen=True, kw_only=True)
class ChannelUpdateData:
    """Mirrors the transport-layer update request; used as a Command field."""

    name: Unsettable[str] = UNSET
    topic: Unsettable[str | None] = UNSET
    position: Unsettable[int] = UNSET


@dataclass(frozen=True, kw_only=True)
class ChannelUpdate(ChannelUpdateData):
    """Persistence payload for a channel update."""


@dataclass(frozen=True, kw_only=True)
class ChannelDTO:
    id: UUID
    name: str
    server_id: UUID
    type: ChannelType
    topic: str | None
    position: int
    last_sequence: int
    is_private: bool
    created_at: datetime
    updated_at: datetime


def channel_to_dto(channel: Channel) -> ChannelDTO:
    return ChannelDTO(
        id=channel.id,
        name=channel.name,
        server_id=channel.server_id,
        type=channel.type,
        topic=channel.topic,
        position=channel.position,
        last_sequence=channel.last_sequence,
        is_private=channel.is_private,
        created_at=channel.created_at,
        updated_at=channel.updated_at,
    )
