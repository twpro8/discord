from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.modules.channels.domain.enums import ChannelType
from src.shared.schemas import BaseSchema


class ChannelResponse(BaseSchema):
    id: UUID
    name: str
    server_id: UUID
    type: ChannelType
    topic: str | None
    position: int
    is_private: bool
    created_at: datetime
    updated_at: datetime


class ChannelCreateRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=128)
    type: ChannelType = ChannelType.text
    topic: str | None = Field(default=None, max_length=1024)
    is_private: bool = False


class ChannelUpdateRequest(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    topic: str | None = Field(default=None, max_length=1024)
    position: int | None = Field(default=None, ge=0)
