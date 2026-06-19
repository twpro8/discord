from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from src.core.schemas import BaseSchema


@dataclass
class AccessTokenPayload:
    sub: UUID


class TokenPair(BaseSchema):
    access_token: str
    refresh_token: str


class UserCreateSchema(BaseSchema):
    """
    Schema for creating a user
    """

    name: str
    username: str
    email: str
    password_hash: str


class UserRegisterSchema(BaseSchema):
    """
    Schema for creating a user
    """

    name: str
    username: str
    email: EmailStr
    password: str


class UserLoginSchema(BaseSchema):
    """
    Schema for login a user
    """

    username: str
    password: str


class RefreshTokenCreateSchema(BaseSchema):
    token_hash: str
    user_id: UUID
    expires_at: datetime


class RefreshTokenSchema(BaseSchema):
    id: UUID
    user_id: UUID
    is_revoked: bool
    expires_at: datetime
    created_at: datetime


class RefreshToken(BaseSchema):
    refresh_token: str
