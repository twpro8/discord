from uuid import uuid4

import pytest
from fakeredis.aioredis import FakeRedis

from src.modules.presence.adapters.persistence.redis_presence_repository import (
    RedisPresenceRepository,
)
from src.modules.presence.domain.entities.dtos import PresenceStatus


@pytest.fixture
def redis() -> FakeRedis:
    return FakeRedis(decode_responses=True)


async def test_first_connection_transitions_offline_to_online(redis: FakeRedis) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    user_id, conn_id = uuid4(), uuid4()

    transition = await repo.record_connection(user_id, conn_id)

    assert transition.old == PresenceStatus.OFFLINE
    assert transition.new == PresenceStatus.ONLINE
    assert transition.changed


async def test_second_tab_connecting_does_not_report_a_fresh_transition(
    redis: FakeRedis,
) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    user_id = uuid4()

    await repo.record_connection(user_id, uuid4())
    transition = await repo.record_connection(user_id, uuid4())

    assert transition.old == PresenceStatus.ONLINE
    assert transition.new == PresenceStatus.ONLINE
    assert not transition.changed


async def test_all_connections_idle_transitions_to_away(redis: FakeRedis) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    user_id, conn_id = uuid4(), uuid4()
    await repo.record_connection(user_id, conn_id)

    transition = await repo.renew_connection(user_id, conn_id, idle=True)

    assert transition.old == PresenceStatus.ONLINE
    assert transition.new == PresenceStatus.AWAY


async def test_one_active_connection_among_idle_ones_keeps_status_online(
    redis: FakeRedis,
) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    user_id = uuid4()
    conn_a, conn_b = uuid4(), uuid4()
    await repo.record_connection(user_id, conn_a)
    await repo.record_connection(user_id, conn_b)

    await repo.renew_connection(user_id, conn_a, idle=True)
    transition = await repo.renew_connection(user_id, conn_b, idle=True)

    assert transition.new == PresenceStatus.AWAY

    # conn_a becomes active again — should flip back to online even though
    # conn_b is still idle.
    transition = await repo.renew_connection(user_id, conn_a, idle=False)
    assert transition.old == PresenceStatus.AWAY
    assert transition.new == PresenceStatus.ONLINE


async def test_removing_last_connection_transitions_to_offline_and_records_last_seen(
    redis: FakeRedis,
) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    user_id, conn_id = uuid4(), uuid4()
    await repo.record_connection(user_id, conn_id)

    transition = await repo.remove_connection(user_id, conn_id)

    assert transition.new == PresenceStatus.OFFLINE
    statuses = await repo.get_statuses({user_id})
    assert statuses[user_id].status == PresenceStatus.OFFLINE
    assert statuses[user_id].last_seen_at is not None


async def test_removing_one_of_several_connections_does_not_go_offline(
    redis: FakeRedis,
) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    user_id = uuid4()
    conn_a, conn_b = uuid4(), uuid4()
    await repo.record_connection(user_id, conn_a)
    await repo.record_connection(user_id, conn_b)

    transition = await repo.remove_connection(user_id, conn_a)

    assert transition.new == PresenceStatus.ONLINE
    assert not transition.changed


async def test_get_statuses_defaults_unknown_users_to_offline(redis: FakeRedis) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    unknown_user_id = uuid4()

    statuses = await repo.get_statuses({unknown_user_id})

    assert statuses[unknown_user_id].status == PresenceStatus.OFFLINE
    assert statuses[unknown_user_id].last_seen_at is None


async def test_sweep_stale_purges_dead_connections_and_reports_transitions(
    redis: FakeRedis, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=10.0)
    user_id, conn_id = uuid4(), uuid4()

    fake_now = [1_000_000.0]
    monkeypatch.setattr(
        "src.modules.presence.adapters.persistence.redis_presence_repository.time.time",
        lambda: fake_now[0],
    )

    await repo.record_connection(user_id, conn_id)
    assert await repo.list_online_user_ids() == {user_id}

    # Advance time well past the staleness threshold without renewing —
    # simulates a crashed tab that never sent a clean disconnect.
    fake_now[0] += 100.0

    transitioned = await repo.sweep_stale()

    assert transitioned == [user_id]
    assert await repo.list_online_user_ids() == set()
    statuses = await repo.get_statuses({user_id})
    assert statuses[user_id].status == PresenceStatus.OFFLINE


async def test_sweep_stale_leaves_fresh_connections_alone(redis: FakeRedis) -> None:
    repo = RedisPresenceRepository(redis, stale_after_seconds=75.0)
    user_id, conn_id = uuid4(), uuid4()
    await repo.record_connection(user_id, conn_id)

    transitioned = await repo.sweep_stale()

    assert transitioned == []
    assert await repo.list_online_user_ids() == {user_id}
