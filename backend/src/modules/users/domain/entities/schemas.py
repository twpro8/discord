from datetime import datetime
from uuid import UUID

from src.shared.schemas import BaseSchema


class UserCreate(BaseSchema):
    name: str
    username: str
    email: str
    password_hash: str


class UserDeactivate(BaseSchema):
    is_active: bool = False


class UserDTO(BaseSchema):
    """Read-only projection of a User, safe to hand to other modules —
    never carries password_hash."""

    id: UUID
    name: str
    username: str
    email: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
