from typing import Annotated, cast

from fastapi import Depends, HTTPException, status, Header, Cookie, Body
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.auth.schemas import RefreshToken
from src.core.postgres import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


def get_access_token(
    authorization: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Cookie()] = None,
) -> str:
    """get access token"""
    if authorization:
        parts = authorization.split(" ", 1)

        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )

        scheme, token = parts

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )

        return token

    if access_token:
        return access_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You have not provided an access token",
    )


def get_refresh_token(
    token_body: Annotated[RefreshToken | None, Body()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> str:
    """get refresh token"""
    if token_body:
        return token_body.refresh_token

    if refresh_token:
        return refresh_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You have not provided a refresh token",
    )


RedisDep = Annotated[Redis, Depends(get_redis)]
AccessTokenDep = Annotated[str, Depends(get_access_token)]
RefreshTokenDep = Annotated[str, Depends(get_refresh_token)]
