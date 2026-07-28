from re import match
from uuid import UUID

from pydantic import Field, field_validator

from src.modules.channels.domain.enums import ChannelType
from src.shared.schemas import BaseSchema


class ChannelCreateRequest(BaseSchema):
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


class ChannelCreate(ChannelCreateRequest):
    server_id: UUID
