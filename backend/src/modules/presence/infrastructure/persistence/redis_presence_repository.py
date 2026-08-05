import time
from collections.abc import Awaitable
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from redis.asyncio import Redis

from src.modules.presence.domain.entities.dtos import (
    PresenceDTO,
    PresenceStatus,
    PresenceTransition,
)

_ONLINE_USERS_KEY = "presence:online_users"


def _online_key(user_id: UUID) -> str:
    return f"presence:online:{user_id}"


def _idle_key(user_id: UUID) -> str:
    return f"presence:idle:{user_id}"


def _status_key(user_id: UUID) -> str:
    return f"presence:status:{user_id}"


def _last_seen_key(user_id: UUID) -> str:
    return f"presence:last_seen:{user_id}"


class RedisPresenceRepository:
    """Redis-backed, not Postgres — presence is ephemeral/high-frequency and
    doesn't need durable relational storage (see core.realtime.redis_pubsub's
    own docstring flagging this as the anticipated need for presence).

    Deliberately no Lua/WATCH-MULTI-EXEC for the connect/disconnect/heartbeat
    transition detection, despite that being the first-draft plan: every
    write here recomputes the aggregate status from a fresh read of the live
    ZSET+Hash and unconditionally overwrites the cached status string, rather
    than inferring a transition from a mutated counter's exact value (the
    "ZADD then ZCARD == 1" pattern that has a real missed-transition race
    under concurrent connects). Because Redis serializes all commands, the
    chronologically last concurrent caller for a given user always reads the
    true post-mutation state — so this can duplicate a fan-out under a race
    (harmless: presence.update is idempotent, upserted by user_id on the
    client) but can never miss one. The one residual race — a stale read
    finishing its write after a fresher one, leaving `presence:status` one
    step behind — self-corrects on the very next heartbeat or connection
    event, which is an acceptable tradeoff for soft-realtime presence.

    (Also: FakeRedis, used by this codebase's test suite, doesn't support
    Lua EVAL without the optional `lupa` dependency, which isn't installed —
    a second, independent reason to avoid Lua here.)
    """

    def __init__(self, redis: Redis, *, stale_after_seconds: float) -> None:
        self._redis = redis
        self._stale_after_seconds = stale_after_seconds

    async def record_connection(
        self, user_id: UUID, connection_id: UUID
    ) -> PresenceTransition:
        now = time.time()
        conn_id = str(connection_id)
        await self._await_int(self._redis.zadd(_online_key(user_id), {conn_id: now}))
        await self._await_int(self._redis.hset(_idle_key(user_id), conn_id, "0"))
        return await self._recompute_and_store(user_id, now)

    async def remove_connection(
        self, user_id: UUID, connection_id: UUID
    ) -> PresenceTransition:
        now = time.time()
        conn_id = str(connection_id)
        await self._await_int(self._redis.zrem(_online_key(user_id), conn_id))
        await self._await_int(self._redis.hdel(_idle_key(user_id), conn_id))
        return await self._recompute_and_store(user_id, now)

    async def renew_connection(
        self, user_id: UUID, connection_id: UUID, *, idle: bool
    ) -> PresenceTransition:
        now = time.time()
        conn_id = str(connection_id)
        await self._await_int(self._redis.zadd(_online_key(user_id), {conn_id: now}))
        await self._await_int(
            self._redis.hset(_idle_key(user_id), conn_id, "1" if idle else "0")
        )
        return await self._recompute_and_store(user_id, now)

    async def get_statuses(self, user_ids: set[UUID]) -> dict[UUID, PresenceDTO]:
        if not user_ids:
            return {}
        ordered = list(user_ids)
        statuses = await self._await_str_list(
            self._redis.mget([_status_key(uid) for uid in ordered])
        )
        last_seen_values = await self._await_str_list(
            self._redis.mget([_last_seen_key(uid) for uid in ordered])
        )
        result: dict[UUID, PresenceDTO] = {}
        for user_id, raw_status, raw_last_seen in zip(
            ordered, statuses, last_seen_values, strict=True
        ):
            status = (
                PresenceStatus(raw_status) if raw_status else PresenceStatus.OFFLINE
            )
            result[user_id] = PresenceDTO(
                user_id=user_id,
                status=status,
                last_seen_at=_parse_timestamp(raw_last_seen),
            )
        return result

    async def list_online_user_ids(self) -> set[UUID]:
        members = cast(
            "set[str]",
            await cast("Awaitable[Any]", self._redis.smembers(_ONLINE_USERS_KEY)),
        )
        return {UUID(m) for m in members}

    async def sweep_stale(self) -> list[UUID]:
        now = time.time()
        transitioned: list[UUID] = []
        for user_id in await self.list_online_user_ids():
            transition = await self._recompute_and_store(user_id, now)
            if transition.changed and transition.new == PresenceStatus.OFFLINE:
                transitioned.append(user_id)
        return transitioned

    async def _recompute_and_store(
        self, user_id: UUID, now: float
    ) -> PresenceTransition:
        old_raw = await self._await_str_or_none(self._redis.get(_status_key(user_id)))
        old_status = PresenceStatus(old_raw) if old_raw else PresenceStatus.OFFLINE

        online_key = _online_key(user_id)
        idle_key = _idle_key(user_id)
        await self._await_int(
            self._redis.zremrangebyscore(
                online_key, "-inf", now - self._stale_after_seconds
            )
        )
        live_connections = await self._await_str_list(
            self._redis.zrange(online_key, 0, -1)
        )

        if not live_connections:
            new_status = PresenceStatus.OFFLINE
            await self._await_int(self._redis.delete(idle_key))
            await self._await_bool(self._redis.set(_last_seen_key(user_id), now))
            await self._await_int(self._redis.srem(_ONLINE_USERS_KEY, str(user_id)))
        else:
            idle_flags = await self._await_str_list(
                self._redis.hmget(idle_key, live_connections)
            )
            all_idle = all(flag == "1" for flag in idle_flags)
            new_status = PresenceStatus.AWAY if all_idle else PresenceStatus.ONLINE
            await self._await_int(self._redis.sadd(_ONLINE_USERS_KEY, str(user_id)))

        await self._await_bool(self._redis.set(_status_key(user_id), new_status.value))
        return PresenceTransition(old=old_status, new=new_status)

    # redis-py's command mixins are shared between the sync and async
    # clients, so their declared return type is `T | Awaitable[T]` even on
    # `redis.asyncio.Redis` where it's always the latter — these narrow it
    # back for mypy --strict, same rationale as core.cache.cache.RedisCache's
    # `cast` on `get`.
    @staticmethod
    async def _await_int(value: Any) -> int:
        return cast(int, await cast("Awaitable[Any]", value))

    @staticmethod
    async def _await_bool(value: Any) -> bool:
        return cast(bool, await cast("Awaitable[Any]", value))

    @staticmethod
    async def _await_str_or_none(value: Any) -> str | None:
        return cast("str | None", await cast("Awaitable[Any]", value))

    @staticmethod
    async def _await_str_list(value: Any) -> list[str | None]:
        return cast("list[str | None]", await cast("Awaitable[Any]", value))


def _parse_timestamp(raw: str | None) -> datetime | None:
    return datetime.fromtimestamp(float(raw), tz=UTC) if raw else None
