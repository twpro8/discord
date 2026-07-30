from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class RegisterData:
    name: str
    username: str
    email: str
    password: str


@dataclass(frozen=True, kw_only=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True, kw_only=True)
class RefreshTokenCreate:
    user_id: UUID
    token_hash: str
    expires_at: datetime
