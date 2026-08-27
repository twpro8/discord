from datetime import UTC, datetime
from uuid import uuid4

from src.modules.friends.domain.entities.dtos import FriendRequestWithUser
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.usecases.get_friends import GetFriendsUseCase
from tests.unit.friends.fakes import FakeFriendRepository


async def test_returns_repository_friends() -> None:
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
    use_case = GetFriendsUseCase(friends)

    result = await use_case(user_id=uuid4())

    assert result is friends.friends_list
