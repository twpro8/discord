from uuid import uuid4

from src.modules.friends.application.commands.accept_request import (
    AcceptFriendRequestCommand,
    AcceptFriendRequestCommandHandler,
)
from src.modules.friends.domain.entities.schemas import FriendRequestCreate
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from tests.unit.friends.fakes import FakeFriendRepository, FakeFriendUnitOfWork


def _handler() -> tuple[AcceptFriendRequestCommandHandler, FakeFriendRepository]:
    friends = FakeFriendRepository()
    uow = FakeFriendUnitOfWork(friends)
    return AcceptFriendRequestCommandHandler(uow), friends


async def test_rejects_unknown_request() -> None:
    handler, _ = _handler()

    result = await handler.handle(
        AcceptFriendRequestCommand(current_user_id=uuid4(), request_id=uuid4())
    )

    assert result.is_err
    assert isinstance(result.error, FriendRequestNotFoundError)


async def test_rejects_non_participant() -> None:
    handler, friends = _handler()
    sender_id, target_id = uuid4(), uuid4()
    request = await friends.create(
        FriendRequestCreate(user_id=sender_id, target_user_id=target_id)
    )

    result = await handler.handle(
        AcceptFriendRequestCommand(current_user_id=uuid4(), request_id=request.id)
    )

    assert result.is_err
    assert isinstance(result.error, NotParticipantError)


async def test_rejects_already_accepted_request() -> None:
    handler, friends = _handler()
    sender_id, target_id = uuid4(), uuid4()
    request = await friends.create(
        FriendRequestCreate(
            user_id=sender_id, target_user_id=target_id, status=FriendStatus.FRIENDS
        )
    )

    result = await handler.handle(
        AcceptFriendRequestCommand(current_user_id=target_id, request_id=request.id)
    )

    assert result.is_err
    assert isinstance(result.error, FriendRequestNotPendingError)


async def test_accepts_pending_request() -> None:
    handler, friends = _handler()
    sender_id, target_id = uuid4(), uuid4()
    request = await friends.create(
        FriendRequestCreate(user_id=sender_id, target_user_id=target_id)
    )

    result = await handler.handle(
        AcceptFriendRequestCommand(current_user_id=target_id, request_id=request.id)
    )

    assert result.is_ok
    assert result.value.status == FriendStatus.FRIENDS
