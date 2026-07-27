from datetime import datetime
from uuid import UUID

from src.shared.schemas import BaseSchema


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

    def mark_as_inactive(self) -> None:
        self.is_active = False


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
