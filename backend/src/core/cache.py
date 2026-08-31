from typing import Protocol, cast

from redis.asyncio import Redis


class Cache(Protocol):
    """Abstract read-model cache contract. Modules depend on this, not on
    redis.asyncio directly — swapping Redis for something else later
    touches only RedisCache, not any query handler.
    """

    async def get(self, key: str) -> str | None: ...

    async def set(
        self, key: str, value: str, ttl_seconds: int | None = None
    ) -> None: ...

    async def delete(self, key: str) -> None: ...


class RedisCache:
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def get(self, key: str) -> str | None:
        return cast(str | None, await self._client.get(key))

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        await self._client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)
