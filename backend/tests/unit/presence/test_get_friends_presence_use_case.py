from datetime import UTC, datetime
from uuid import uuid4

from src.modules.presence.domain.entities.dtos import PresenceDTO, PresenceStatus
from src.modules.presence.usecases.get_friends_presence import (
    GetFriendsPresenceUseCase,
)
from tests.unit.friends.fakes import FakeFriendsFacade
from tests.unit.presence.fakes import FakePresenceRepository


async def test_returns_presence_only_for_friends() -> None:
    user_id, friend_id, stranger_id = uuid4(), uuid4(), uuid4()
    friends_facade = FakeFriendsFacade({user_id: {friend_id}})
    presence = FakePresenceRepository()
    presence.statuses = {
        friend_id: PresenceDTO(user_id=friend_id, status=PresenceStatus.ONLINE),
        stranger_id: PresenceDTO(user_id=stranger_id, status=PresenceStatus.ONLINE),
    }
    use_case = GetFriendsPresenceUseCase(presence, friends_facade)

    result = await use_case(user_id=user_id)

    assert [dto.user_id for dto in result] == [friend_id]


async def test_no_friends_returns_empty_list() -> None:
    presence = FakePresenceRepository()
    friends_facade = FakeFriendsFacade()
    use_case = GetFriendsPresenceUseCase(presence, friends_facade)

    result = await use_case(user_id=uuid4())

    assert result == []


async def test_includes_last_seen_for_offline_friends() -> None:
    user_id, friend_id = uuid4(), uuid4()
    last_seen = datetime(2026, 1, 1, tzinfo=UTC)
    friends_facade = FakeFriendsFacade({user_id: {friend_id}})
    presence = FakePresenceRepository()
    presence.statuses = {
        friend_id: PresenceDTO(
            user_id=friend_id, status=PresenceStatus.OFFLINE, last_seen_at=last_seen
        )
    }
    use_case = GetFriendsPresenceUseCase(presence, friends_facade)

    result = await use_case(user_id=user_id)

    assert result[0].last_seen_at == last_seen
