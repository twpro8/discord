from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from src.core.schemas import BaseSchema


class RegisterForm(BaseSchema):
    name: str
    username: str
    email: EmailStr
    password: str


class TokenPair(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenCreate(BaseSchema):
    user_id: UUID
    token_hash: str
    expires_at: datetime


class RefreshToken(BaseSchema):
    id: UUID
    user_id: UUID
    is_revoked: bool
    expires_at: datetime
    created_at: datetime
