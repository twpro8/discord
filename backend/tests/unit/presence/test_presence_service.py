import json
from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.realtime.envelope import EventType
from src.core.realtime.rooms import server_room, user_room
from src.modules.presence.application.presence_service import PresenceService
from src.modules.presence.domain.entities.dtos import (
    PresenceDTO,
    PresenceStatus,
    PresenceTransition,
)
from tests.unit.presence.fakes import FakePresenceRepository, FakeRealtimeNotifier


def _make_service(
    presence: FakePresenceRepository,
    notifier: FakeRealtimeNotifier,
    *,
    friend_ids: Iterable[UUID] = (),
    server_ids: Iterable[UUID] = (),
    raise_on_lookup: bool = False,
) -> PresenceService:
    async def lookup(_user_id: UUID) -> tuple[set[UUID], set[UUID]]:
        if raise_on_lookup:
            raise RuntimeError("boom")
        return set(friend_ids), set(server_ids)

    return PresenceService(presence, notifier, lookup)


async def test_mark_connection_online_fans_out_to_friends_and_servers_on_transition() -> (
    None
):
    presence = FakePresenceRepository()
    notifier = FakeRealtimeNotifier()
    friend_id, server_id = uuid4(), uuid4()
    service = _make_service(
        presence, notifier, friend_ids={friend_id}, server_ids={server_id}
    )
    user_id, conn_id = uuid4(), uuid4()

    await service.mark_connection_online(user_id, conn_id)

    rooms_notified = {room for room, _, _ in notifier.published}
    assert rooms_notified == {user_room(friend_id), server_room(server_id)}
    for _room, event_type, payload in notifier.published:
        assert event_type == EventType.PRESENCE_UPDATE
        assert payload["user_id"] == str(user_id)
        assert payload["status"] == "online"
        assert payload["last_seen_at"] is None


async def test_second_tab_connecting_does_not_fan_out_again() -> None:
    presence = FakePresenceRepository()
    presence.record_connection_result = PresenceTransition(
        old=PresenceStatus.ONLINE, new=PresenceStatus.ONLINE
    )
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier, friend_ids={uuid4()})

    await service.mark_connection_online(uuid4(), uuid4())

    assert notifier.published == []


async def test_mark_connection_offline_includes_last_seen_in_payload() -> None:
    presence = FakePresenceRepository()
    notifier = FakeRealtimeNotifier()
    friend_id = uuid4()
    service = _make_service(presence, notifier, friend_ids={friend_id})
    user_id, conn_id = uuid4(), uuid4()
    last_seen = datetime(2026, 1, 1, tzinfo=UTC)
    presence.statuses[user_id] = PresenceDTO(
        user_id=user_id, status=PresenceStatus.OFFLINE, last_seen_at=last_seen
    )

    await service.mark_connection_offline(user_id, conn_id)

    assert len(notifier.published) == 1
    _, _, payload = notifier.published[0]
    assert payload["status"] == "offline"
    assert payload["last_seen_at"] == last_seen.isoformat()


async def test_on_activity_parses_heartbeat_idle_flag() -> None:
    presence = FakePresenceRepository()
    presence.renew_connection_result = PresenceTransition(
        old=PresenceStatus.ONLINE, new=PresenceStatus.ONLINE
    )
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier)
    user_id, conn_id = uuid4(), uuid4()

    await service.on_activity(
        user_id, conn_id, json.dumps({"type": "heartbeat", "idle": True})
    )

    assert presence.renew_calls == [(user_id, conn_id, True)]


async def test_on_activity_defaults_malformed_frame_to_not_idle() -> None:
    presence = FakePresenceRepository()
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier)
    user_id, conn_id = uuid4(), uuid4()

    await service.on_activity(user_id, conn_id, "not json at all {{{")

    assert presence.renew_calls == [(user_id, conn_id, False)]


async def test_on_activity_ignores_non_heartbeat_frames() -> None:
    presence = FakePresenceRepository()
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier)
    user_id, conn_id = uuid4(), uuid4()

    await service.on_activity(
        user_id, conn_id, json.dumps({"type": "something_else", "idle": True})
    )

    assert presence.renew_calls == [(user_id, conn_id, False)]


async def test_sweep_stale_fans_out_offline_for_each_transitioned_user() -> None:
    presence = FakePresenceRepository()
    user_a, user_b = uuid4(), uuid4()
    presence.sweep_stale_result = [user_a, user_b]
    friend_of_a = uuid4()
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier, friend_ids={friend_of_a})

    await service.sweep_stale()

    # lookup() is the same fixed fan-out target for both in this test setup
    rooms_notified = [room for room, _, _ in notifier.published]
    assert rooms_notified.count(user_room(friend_of_a)) == 2


async def test_repository_failure_does_not_propagate() -> None:
    presence = FakePresenceRepository()
    presence.raise_on_record = True
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier)

    await service.mark_connection_online(uuid4(), uuid4())  # must not raise

    assert notifier.published == []


async def test_sweep_failure_does_not_propagate() -> None:
    presence = FakePresenceRepository()
    presence.raise_on_sweep = True
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier)

    await service.sweep_stale()  # must not raise


async def test_lookup_failure_is_swallowed_and_no_fan_out_happens() -> None:
    presence = FakePresenceRepository()
    notifier = FakeRealtimeNotifier()
    service = _make_service(presence, notifier, raise_on_lookup=True)

    await service.mark_connection_online(uuid4(), uuid4())  # must not raise

    assert notifier.published == []


async def test_notifier_failure_for_one_room_does_not_block_others() -> None:
    presence = FakePresenceRepository()
    notifier = FakeRealtimeNotifier()
    friend_id, server_id = uuid4(), uuid4()
    notifier.raise_for_rooms = {user_room(friend_id)}
    service = _make_service(
        presence, notifier, friend_ids={friend_id}, server_ids={server_id}
    )

    await service.mark_connection_online(uuid4(), uuid4())  # must not raise

    rooms_notified = {room for room, _, _ in notifier.published}
    assert rooms_notified == {server_room(server_id)}
