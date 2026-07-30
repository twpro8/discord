from src.modules.friends.application.commands.send_request import (
    SendFriendRequestCommand,
    SendFriendRequestCommandHandler,
)
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
from src.modules.users.domain.entities.user import User
from tests.unit.friends.fakes import (
    FakeFriendRepository,
    FakeFriendUnitOfWork,
    FakeUsersFacade,
    make_user,
)


def _handler(
    users: list[User] | None = None,
) -> tuple[SendFriendRequestCommandHandler, FakeFriendRepository]:
    friends = FakeFriendRepository()
    uow = FakeFriendUnitOfWork(friends)
    return SendFriendRequestCommandHandler(uow, FakeUsersFacade(users)), friends


async def test_rejects_unknown_username() -> None:
    handler, _ = _handler()

    result = await handler.handle(
        SendFriendRequestCommand(
            sender_id=make_user("me").id,
            data=SendFriendRequestData(username="ghost"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, TargetUserNotFoundError)


async def test_rejects_self_request() -> None:
    me = make_user("myself")
    handler, _ = _handler([me])

    result = await handler.handle(
        SendFriendRequestCommand(
            sender_id=me.id,
            data=SendFriendRequestData(username="myself"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, CannotSendFriendRequestToSelfError)


async def test_rejects_duplicate_relationship() -> None:
    me, target = make_user("me"), make_user("target")
    handler, friends = _handler([me, target])
    await friends.create(FriendRequestCreate(user_id=me.id, target_user_id=target.id))

    result = await handler.handle(
        SendFriendRequestCommand(
            sender_id=me.id,
            data=SendFriendRequestData(username="target"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, FriendRequestAlreadyExistsError)


async def test_creates_pending_request() -> None:
    me, target = make_user("me"), make_user("target")
    handler, friends = _handler([me, target])

    result = await handler.handle(
        SendFriendRequestCommand(
            sender_id=me.id,
            data=SendFriendRequestData(username="target"),
        )
    )

    assert result.is_ok
    request = result.value
    assert request.status == FriendStatus.PENDING
    assert request.user_id == me.id
    assert request.target_user_id == target.id
