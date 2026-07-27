from typing import Annotated, cast

from fastapi import Depends
from fastapi.requests import Request
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.shared.application.mediator import Mediator

access_cookie_scheme = APIKeyCookie(name="access_token")


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


def get_mediator(request: Request) -> Mediator:
    return cast(Mediator, request.app.state.container.mediator)


SessionDep = Annotated[AsyncSession, Depends(get_session)]
MediatorDep = Annotated[Mediator, Depends(get_mediator)]
RedisDep = Annotated[Redis, Depends(get_redis)]
AccessTokenDep = Annotated[str, Depends(access_cookie_scheme)]
