from datetime import UTC, datetime
from uuid import uuid4

from src.modules.friends.application.queries.get_friends import (
    GetFriendsQuery,
    GetFriendsQueryHandler,
)
from src.modules.friends.domain.entities.schemas import FriendRequestWithUser
from src.modules.friends.domain.enums import FriendStatus
from tests.unit.friends.fakes import FakeFriendRepository


async def test_returns_repository_friends_wrapped_in_ok() -> None:
    friends = FakeFriendRepository()
    now = datetime.now(UTC)
    friends.friends_list = [
        FriendRequestWithUser(
            id=uuid4(),
            user_id=uuid4(),
            target_user_id=uuid4(),
            status=FriendStatus.FRIENDS,
            created_at=now,
            updated_at=now,
            username="target",
            avatar_url=None,
        )
    ]
    handler = GetFriendsQueryHandler(friends)

    result = await handler.handle(GetFriendsQuery(user_id=uuid4()))

    assert result.is_ok
    assert result.value is friends.friends_list
