from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack
from typing import Annotated, cast

from fastapi import Depends
from fastapi.requests import Request
from fastapi.security import APIKeyCookie
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.modules.chats.composition import register_chat_handlers
from src.modules.friends.composition import register_friend_handlers
from src.shared.application.in_process_mediator import InProcessMediator
from src.shared.application.mediator import Mediator

access_cookie_scheme = APIKeyCookie(name="access_token")


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_mediator(session: SessionDep) -> AsyncGenerator[Mediator]:
    async with AsyncExitStack() as stack:
        mediator = InProcessMediator()
        await register_chat_handlers(mediator, session, stack)
        await register_friend_handlers(mediator, session, stack)
        yield mediator


MediatorDep = Annotated[Mediator, Depends(get_mediator)]
RedisDep = Annotated[Redis, Depends(get_redis)]
AccessTokenDep = Annotated[str, Depends(access_cookie_scheme)]
