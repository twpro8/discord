from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.shared.schemas import BaseSchema


class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=3, max_length=64)
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr = Field(min_length=3, max_length=32)
    password: str = Field(min_length=3, max_length=128)


class UserRegisterResponse(BaseModel):
    id: UUID


class UserUpdateRequest(BaseSchema):
    name: str | None = Field(None, max_length=64)
    username: str | None = Field(None, min_length=3, max_length=32)
    email: EmailStr | None = Field(None, min_length=3, max_length=32)


class UserResponse(BaseSchema):
    id: UUID
    name: str
    username: str
    email: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
