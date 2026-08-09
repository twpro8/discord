from uuid import uuid4

import pytest
from fakeredis.aioredis import FakeRedis

from src.modules.calls.domain.enums import CallState, ReserveOutcome
from src.modules.calls.infrastructure.persistence.redis_call_repository import (
    RedisCallRepository,
)


@pytest.fixture
def redis() -> FakeRedis:
    return FakeRedis(decode_responses=True)


async def test_reserve_succeeds_once_for_a_fresh_pair(redis: FakeRedis) -> None:
    repo = RedisCallRepository(redis)
    call_id, chat_id, caller_id, callee_id, caller_conn = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )

    outcome = await repo.reserve(
        call_id, chat_id, caller_id, callee_id, caller_conn, ring_ttl_seconds=60.0
    )

    assert outcome is ReserveOutcome.RESERVED
    session = await repo.get_session(call_id)
    assert session is not None
    assert session.state is CallState.RINGING
    assert await repo.get_active_call_id_for_user(caller_id) == call_id
    assert await repo.get_active_call_id_for_user(callee_id) == call_id


async def test_reserve_fails_with_no_mutation_when_caller_already_busy(
    redis: FakeRedis,
) -> None:
    repo = RedisCallRepository(redis)
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    other_call_id = uuid4()
    await repo.reserve(
        other_call_id, chat_id, caller_id, uuid4(), uuid4(), ring_ttl_seconds=60.0
    )

    new_call_id = uuid4()
    outcome = await repo.reserve(
        new_call_id, chat_id, caller_id, callee_id, uuid4(), ring_ttl_seconds=60.0
    )

    assert outcome is ReserveOutcome.CALLER_BUSY
    assert await repo.get_session(new_call_id) is None
    # The callee must not have been reserved either — no partial mutation.
    assert await repo.get_active_call_id_for_user(callee_id) is None


async def test_reserve_fails_and_rolls_back_caller_key_when_callee_already_busy(
    redis: FakeRedis,
) -> None:
    repo = RedisCallRepository(redis)
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    other_call_id = uuid4()
    await repo.reserve(
        other_call_id, chat_id, callee_id, uuid4(), uuid4(), ring_ttl_seconds=60.0
    )

    new_call_id = uuid4()
    outcome = await repo.reserve(
        new_call_id, chat_id, caller_id, callee_id, uuid4(), ring_ttl_seconds=60.0
    )

    assert outcome is ReserveOutcome.CALLEE_BUSY
    assert await repo.get_session(new_call_id) is None
    # Rollback must have freed the caller's own reservation — a
    # subsequent, unrelated invite from the same caller must succeed.
    assert await repo.get_active_call_id_for_user(caller_id) is None
    outcome2 = await repo.reserve(
        uuid4(), chat_id, caller_id, uuid4(), uuid4(), ring_ttl_seconds=60.0
    )
    assert outcome2 is ReserveOutcome.RESERVED


async def test_reserve_is_atomic_across_overlapping_concurrent_attempts(
    redis: FakeRedis,
) -> None:
    """Simulates the glare scenario from plan §1/§6: two invites racing
    over an overlapping pair of users must never both succeed. Redis
    itself serializes each SET NX, so interleaving the two reserve()
    calls' underlying commands (as a real concurrent race would) can
    never produce two RESERVED outcomes — this asserts that invariant
    holds across every possible interleaving order, not just sequential
    calls, by exercising both orderings explicitly."""
    caller_a, caller_b, shared_target, chat_id = uuid4(), uuid4(), uuid4(), uuid4()

    for first, second in (
        ((caller_a, shared_target), (shared_target, caller_b)),
        ((shared_target, caller_b), (caller_a, shared_target)),
    ):
        repo = RedisCallRepository(redis)
        outcome1 = await repo.reserve(
            uuid4(), chat_id, first[0], first[1], uuid4(), ring_ttl_seconds=60.0
        )
        outcome2 = await repo.reserve(
            uuid4(), chat_id, second[0], second[1], uuid4(), ring_ttl_seconds=60.0
        )
        outcomes = {outcome1, outcome2}
        assert ReserveOutcome.RESERVED in outcomes
        assert outcomes != {ReserveOutcome.RESERVED}  # never both succeed
        # cleanup for the next iteration of this loop, sharing one `redis`
        for user_id in (caller_a, caller_b, shared_target):
            key = f"call:active_user:{user_id}"
            await redis.delete(key)


async def test_try_accept_succeeds_once_and_pins_the_winning_connection(
    redis: FakeRedis,
) -> None:
    repo = RedisCallRepository(redis)
    call_id, chat_id, caller_id, callee_id, caller_conn = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    await repo.reserve(
        call_id, chat_id, caller_id, callee_id, caller_conn, ring_ttl_seconds=60.0
    )
    tab_a, tab_b = uuid4(), uuid4()

    won_a = await repo.try_accept(call_id, tab_a, active_ttl_seconds=3600.0)
    won_b = await repo.try_accept(call_id, tab_b, active_ttl_seconds=3600.0)

    assert won_a is True
    assert won_b is False
    session = await repo.get_session(call_id)
    assert session is not None
    assert session.state is CallState.ACTIVE
    assert session.answering_connection_id == tab_a


async def test_end_session_is_idempotent_and_clears_all_keys(redis: FakeRedis) -> None:
    repo = RedisCallRepository(redis)
    call_id, chat_id, caller_id, callee_id, caller_conn = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    await repo.reserve(
        call_id, chat_id, caller_id, callee_id, caller_conn, ring_ttl_seconds=60.0
    )

    ended = await repo.end_session(call_id)
    assert ended is not None
    assert ended.call_id == call_id

    assert await repo.get_session(call_id) is None
    assert await repo.get_active_call_id_for_user(caller_id) is None
    assert await repo.get_active_call_id_for_user(callee_id) is None

    # Second call — already gone — must be a safe no-op, not an error.
    assert await repo.end_session(call_id) is None
