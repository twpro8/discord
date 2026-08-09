import json
from collections.abc import Awaitable
from datetime import UTC, datetime
from typing import Any, cast
from uuid import UUID

from redis.asyncio import Redis

from src.modules.calls.domain.entities.call_session import CallSession
from src.modules.calls.domain.enums import CallState, ReserveOutcome


def _active_user_key(user_id: UUID) -> str:
    return f"call:active_user:{user_id}"


def _session_key(call_id: UUID) -> str:
    return f"call:session:{call_id}"


def _accept_marker_key(call_id: UUID) -> str:
    return f"call:accept:{call_id}"


def _serialize(session: CallSession) -> str:
    return json.dumps(
        {
            "call_id": str(session.call_id),
            "chat_id": str(session.chat_id),
            "caller_id": str(session.caller_id),
            "callee_id": str(session.callee_id),
            "caller_connection_id": str(session.caller_connection_id),
            "answering_connection_id": (
                str(session.answering_connection_id)
                if session.answering_connection_id
                else None
            ),
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
        }
    )


def _deserialize(raw: str) -> CallSession:
    data = json.loads(raw)
    return CallSession(
        call_id=UUID(data["call_id"]),
        chat_id=UUID(data["chat_id"]),
        caller_id=UUID(data["caller_id"]),
        callee_id=UUID(data["callee_id"]),
        caller_connection_id=UUID(data["caller_connection_id"]),
        answering_connection_id=(
            UUID(data["answering_connection_id"])
            if data["answering_connection_id"]
            else None
        ),
        state=CallState(data["state"]),
        created_at=datetime.fromisoformat(data["created_at"]),
    )


class RedisCallRepository:
    """Redis-only, ephemeral — mirrors RedisPresenceRepository's rationale
    for storing transient/high-frequency state outside Postgres (see that
    class's docstring). Every mutating method is built from atomic
    single-key `SET ... NX EX` operations, deliberately avoiding a
    read-then-write check for the busy/reservation logic: two concurrent
    `reserve()` calls racing over the same user can't both succeed,
    because Redis serializes commands and `SET NX` is atomic per key —
    whichever call's SET NX lands first wins that key outright, and the
    loser's own SET NX simply fails without ever having mutated anything.

    The `reserve()` rollback (DELETE the caller's key if the callee's
    reservation fails) doesn't need a compare-and-delete: only the call
    that successfully SET NX'd a key could ever be the one to free it,
    since no other concurrent `reserve()` could have raced in and
    overwritten it in between (their own SET NX on that same key would
    have failed instead). This is the same single-writer-per-key
    reasoning RedisPresenceRepository's own docstring uses to justify
    skipping Lua/WATCH-MULTI-EXEC — also required here since this
    codebase's pinned `fakeredis` test double can't run Lua EVAL without
    the unavailable `lupa` dependency (see that docstring).
    """

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def reserve(
        self,
        call_id: UUID,
        chat_id: UUID,
        caller_id: UUID,
        callee_id: UUID,
        caller_connection_id: UUID,
        *,
        ring_ttl_seconds: float,
    ) -> ReserveOutcome:
        caller_key = _active_user_key(caller_id)
        caller_ok = await self._set_nx(caller_key, str(call_id), ring_ttl_seconds)
        if not caller_ok:
            return ReserveOutcome.CALLER_BUSY

        callee_key = _active_user_key(callee_id)
        callee_ok = await self._set_nx(callee_key, str(call_id), ring_ttl_seconds)
        if not callee_ok:
            # Safe unconditional rollback — see class docstring.
            await self._await_int(self._redis.delete(caller_key))
            return ReserveOutcome.CALLEE_BUSY

        session = CallSession(
            call_id=call_id,
            chat_id=chat_id,
            caller_id=caller_id,
            callee_id=callee_id,
            caller_connection_id=caller_connection_id,
            answering_connection_id=None,
            state=CallState.RINGING,
            created_at=datetime.now(UTC),
        )
        await self._set_nx(_session_key(call_id), _serialize(session), ring_ttl_seconds)
        return ReserveOutcome.RESERVED

    async def get_session(self, call_id: UUID) -> CallSession | None:
        raw = await self._await_str_or_none(self._redis.get(_session_key(call_id)))
        return _deserialize(raw) if raw else None

    async def get_active_call_id_for_user(self, user_id: UUID) -> UUID | None:
        raw = await self._await_str_or_none(self._redis.get(_active_user_key(user_id)))
        return UUID(raw) if raw else None

    async def try_accept(
        self,
        call_id: UUID,
        connection_id: UUID,
        *,
        active_ttl_seconds: float,
    ) -> bool:
        marker_ok = await self._set_nx(
            _accept_marker_key(call_id), str(connection_id), active_ttl_seconds
        )
        if not marker_ok:
            return False

        session = await self.get_session(call_id)
        if session is None:
            # Session vanished between the marker win and this read (e.g.
            # a near-simultaneous timeout/disconnect) — nothing to accept.
            return False

        updated = CallSession(
            call_id=session.call_id,
            chat_id=session.chat_id,
            caller_id=session.caller_id,
            callee_id=session.callee_id,
            caller_connection_id=session.caller_connection_id,
            answering_connection_id=connection_id,
            state=CallState.ACTIVE,
            created_at=session.created_at,
        )
        await self._await_bool(
            self._redis.set(
                _session_key(call_id), _serialize(updated), ex=int(active_ttl_seconds)
            )
        )
        await self._await_bool(
            self._redis.expire(
                _active_user_key(session.caller_id), int(active_ttl_seconds)
            )
        )
        await self._await_bool(
            self._redis.expire(
                _active_user_key(session.callee_id), int(active_ttl_seconds)
            )
        )
        return True

    async def end_session(self, call_id: UUID) -> CallSession | None:
        session = await self.get_session(call_id)
        if session is None:
            return None
        await self._await_int(
            self._redis.delete(
                _session_key(call_id),
                _active_user_key(session.caller_id),
                _active_user_key(session.callee_id),
            )
        )
        return session

    async def _set_nx(self, key: str, value: str, ttl_seconds: float) -> bool:
        result = await self._await_bool_or_none(
            self._redis.set(key, value, nx=True, ex=int(ttl_seconds))
        )
        return bool(result)

    # redis-py's command mixins are shared between the sync and async
    # clients, so their declared return type is `T | Awaitable[T]` even on
    # `redis.asyncio.Redis` where it's always the latter — these narrow it
    # back for mypy --strict, same rationale as RedisPresenceRepository's
    # own `_await_*` helpers (infrastructure.persistence.
    # redis_presence_repository).
    @staticmethod
    async def _await_int(value: Any) -> int:
        return cast(int, await cast("Awaitable[Any]", value))

    @staticmethod
    async def _await_bool(value: Any) -> bool:
        return cast(bool, await cast("Awaitable[Any]", value))

    @staticmethod
    async def _await_bool_or_none(value: Any) -> bool | None:
        return cast("bool | None", await cast("Awaitable[Any]", value))

    @staticmethod
    async def _await_str_or_none(value: Any) -> str | None:
        return cast("str | None", await cast("Awaitable[Any]", value))
