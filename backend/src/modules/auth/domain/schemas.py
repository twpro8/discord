from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from src.shared.schemas import BaseSchema


class RegisterForm(BaseSchema):
    name: str = Field(min_length=3, max_length=64)
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr = Field(min_length=3, max_length=32)
    password: str = Field(min_length=3, max_length=128)


class LoginForm(BaseSchema):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=3, max_length=128)


class TokenPair(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenCreate(BaseSchema):
    user_id: UUID
    token_hash: str
    expires_at: datetime
