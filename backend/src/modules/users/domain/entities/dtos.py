from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.users.domain.entities.user import User
from src.shared.domain.unset import UNSET, Unsettable


@dataclass(frozen=True, kw_only=True)
class UserUpdate:
    """Persistence payload for a user. `avatar_url`/`password_hash` are set
    by their dedicated commands, never through the transport `UserUpdateRequest`."""

    name: Unsettable[str] = UNSET
    username: Unsettable[str] = UNSET
    email: Unsettable[str] = UNSET
    password_hash: Unsettable[str] = UNSET
    avatar_url: Unsettable[str] = UNSET
    is_active: Unsettable[bool] = UNSET


@dataclass(frozen=True, kw_only=True)
class UserDTO:
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


def user_to_dto(user: User) -> UserDTO:
    return UserDTO(
        id=user.id,
        name=user.name,
        username=str(user.username),
        email=str(user.email),
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
