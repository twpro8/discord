import secrets
from uuid import UUID

import jwt
import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from pwdlib import PasswordHash

from src.core.config import settings
from src.auth.schemas import AccessTokenPayload

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Function for generating hashed password
    :param password: user password
    :return: hashed password
    """
    return password_hash.hash(password)


def hash_token(token: str) -> str:
    """
    Function for generating hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Function for verifying hashed password
    :param plain_password: not hash password
    :param hashed_password: user hash password
    :return: bool
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(payload: AccessTokenPayload) -> str:
    """
    Function for creating access token
    :param payload: data for token
    :return: access token
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token_data = {"sub": str(payload.sub), "exp": expire}
    return jwt.encode(
        token_data,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token() -> tuple[str, str]:
    """Function for creating refresh token"""
    refresh_token_raw = secrets.token_urlsafe(48)
    refresh_token_hash = hash_token(refresh_token_raw)

    return refresh_token_raw, refresh_token_hash


def decode_token(token: str) -> AccessTokenPayload:
    """
    Function for decoding token
    :param token: access token
    """
    try:
        raw_payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM,
        )
        sub = UUID(raw_payload.get("sub")) if raw_payload.get("sub") else None
        if sub is None:
            raise ValueError("No sub UUID provided")
        return AccessTokenPayload(sub=sub)
    except jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT"
        )
