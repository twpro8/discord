from datetime import datetime
from uuid import UUID

from pydantic import Field, EmailStr

from src.core.schemas import BaseSchema


class User(BaseSchema):
    id: UUID
    name: str
    username: str
    email: str
    password_hash: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserRead(BaseSchema):
    id: UUID
    name: str
    username: str
    email: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseSchema):
    name: str
    username: str
    email: str
    password_hash: str


class UserUpdateRequest(BaseSchema):
    name: str | None = Field(None, max_length=64)
    username: str | None = Field(None, min_length=3, max_length=32)
    email: EmailStr | None = Field(None, min_length=3, max_length=32)
