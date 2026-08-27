import pytest

from src.modules.friends.domain.entities.dtos import (
    FriendRequestCreate,
    SendFriendRequestData,
)
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    CannotSendFriendRequestToSelfError,
    FriendRequestAlreadyExistsError,
    TargetUserNotFoundError,
)
from src.modules.friends.usecases.send_request import SendFriendRequestUseCase
from src.modules.users.domain.entities.user import User
from tests.unit.friends.fakes import (
    FakeFriendRepository,
    FakeUsersFacade,
    make_user,
)


def _use_case(
    users: list[User] | None = None,
) -> tuple[SendFriendRequestUseCase, FakeFriendRepository]:
    friends = FakeFriendRepository()
    return SendFriendRequestUseCase(friends, FakeUsersFacade(users)), friends


async def test_rejects_unknown_username() -> None:
    use_case, _ = _use_case()

    with pytest.raises(TargetUserNotFoundError):
        await use_case(
            sender_id=make_user("mem").id,
            data=SendFriendRequestData(username="ghost"),
        )


async def test_rejects_self_request() -> None:
    me = make_user("myself")
    use_case, _ = _use_case([me])

    with pytest.raises(CannotSendFriendRequestToSelfError):
        await use_case(
            sender_id=me.id,
            data=SendFriendRequestData(username="myself"),
        )


async def test_rejects_duplicate_relationship() -> None:
    me, target = make_user("mem"), make_user("target")
    use_case, friends = _use_case([me, target])
    await friends.create(FriendRequestCreate(user_id=me.id, target_user_id=target.id))

    with pytest.raises(FriendRequestAlreadyExistsError):
        await use_case(
            sender_id=me.id,
            data=SendFriendRequestData(username="target"),
        )


async def test_creates_pending_request() -> None:
    me, target = make_user("mem"), make_user("target")
    use_case, _friends = _use_case([me, target])

    request = await use_case(
        sender_id=me.id,
        data=SendFriendRequestData(username="target"),
    )

    assert request.status == FriendStatus.PENDING
    assert request.user_id == me.id
    assert request.target_user_id == target.id
