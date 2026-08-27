from uuid import uuid4

import pytest

from src.modules.friends.domain.entities.dtos import FriendRequestCreate
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from src.modules.friends.usecases.accept_request import AcceptFriendRequestUseCase
from tests.unit.friends.fakes import FakeFriendRepository


def _use_case() -> tuple[AcceptFriendRequestUseCase, FakeFriendRepository]:
    friends = FakeFriendRepository()
    return AcceptFriendRequestUseCase(friends), friends


async def test_rejects_unknown_request() -> None:
    use_case, _ = _use_case()

    with pytest.raises(FriendRequestNotFoundError):
        await use_case(current_user_id=uuid4(), request_id=uuid4())


async def test_rejects_non_participant() -> None:
    use_case, friends = _use_case()
    sender_id, target_id = uuid4(), uuid4()
    request = await friends.create(
        FriendRequestCreate(user_id=sender_id, target_user_id=target_id)
    )

    with pytest.raises(NotParticipantError):
        await use_case(current_user_id=uuid4(), request_id=request.id)


async def test_rejects_already_accepted_request() -> None:
    use_case, friends = _use_case()
    sender_id, target_id = uuid4(), uuid4()
    request = await friends.create(
        FriendRequestCreate(
            user_id=sender_id, target_user_id=target_id, status=FriendStatus.FRIENDS
        )
    )

    with pytest.raises(FriendRequestNotPendingError):
        await use_case(current_user_id=target_id, request_id=request.id)


async def test_accepts_pending_request() -> None:
    use_case, friends = _use_case()
    sender_id, target_id = uuid4(), uuid4()
    request = await friends.create(
        FriendRequestCreate(user_id=sender_id, target_user_id=target_id)
    )

    updated = await use_case(current_user_id=target_id, request_id=request.id)

    assert updated.status == FriendStatus.FRIENDS
