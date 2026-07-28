from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.modules.channels.domain.enums import ChannelType
from src.shared.schemas import BaseSchema


class Channel(BaseSchema):
    id: UUID
    name: str = Field(..., min_length=2, max_length=100)
    server_id: UUID
    type: ChannelType
    topic: str | None
    position: int
    last_sequence: int
    is_private: bool
    created_at: datetime
    updated_at: datetime
