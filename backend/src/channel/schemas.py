from datetime import datetime
from re import match
from uuid import UUID

from pydantic import Field, field_validator
from src.channel.enums import ChannelType
from src.core.schemas import BaseSchema


class ChannelSchema(BaseSchema):
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


class ChannelCreateRequestSchema(BaseSchema):
    name: str = Field(..., min_length=2, max_length=100)
    type: ChannelType = ChannelType.text
    topic: str | None = Field(None, max_length=1024)
    position: int | None = Field(None, ge=0)
    is_private: bool = False

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        if not match(r"^[a-z0-9_-]+$", v):
            raise ValueError("name must match ^[a-z0-9_-]+$")
        return v


class ChannelCreateSchema(ChannelCreateRequestSchema):
    server_id: UUID
