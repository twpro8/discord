from uuid import uuid4

import pytest

from src.core.realtime.rooms import server_room
from src.modules.servers.domain.entities.dtos import (
    ServerCreate,
    ServerInviteCreate,
    ServerMemberCreate,
)
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import ServerInviteNotFoundError
from src.modules.servers.usecases.join_server import JoinServerUseCase
from tests.unit.servers.fakes import (
    FakeRoomMembershipUpdater,
    FakeServerInviteRepository,
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServerUnitOfWork,
)


async def test_unknown_code_is_rejected() -> None:
    uow = FakeServerUnitOfWork(
        FakeServerRepository(),
        FakeServerMemberRepository(),
        FakeServerInviteRepository(),
    )
    use_case = JoinServerUseCase(uow, FakeRoomMembershipUpdater())

    with pytest.raises(ServerInviteNotFoundError):
        await use_case(user_id=uuid4(), code="nope")


async def test_joins_server_and_joins_room() -> None:
    servers = FakeServerRepository()
    members = FakeServerMemberRepository()
    invites = FakeServerInviteRepository()
    uow = FakeServerUnitOfWork(servers, members, invites)
    room_membership_updater = FakeRoomMembershipUpdater()
    use_case = JoinServerUseCase(uow, room_membership_updater)

    server = await servers.create(ServerCreate(name="S", owner_id=uuid4()))
    invite = await invites.create(
        ServerInviteCreate(
            server_id=server.id,
            code="abc123",
            created_by=server.owner_id,
            max_uses=None,
            expires_at=None,
        )
    )
    user_id = uuid4()

    member = await use_case(user_id=user_id, code=invite.code)

    assert member.user_id == user_id
    assert uow.committed
    assert room_membership_updater.joined == [(user_id, server_room(server.id))]


async def test_already_member_still_rejoins_room_without_duplicating_membership() -> (
    None
):
    servers = FakeServerRepository()
    members = FakeServerMemberRepository()
    invites = FakeServerInviteRepository()
    uow = FakeServerUnitOfWork(servers, members, invites)
    room_membership_updater = FakeRoomMembershipUpdater()
    use_case = JoinServerUseCase(uow, room_membership_updater)

    server = await servers.create(ServerCreate(name="S", owner_id=uuid4()))
    invite = await invites.create(
        ServerInviteCreate(
            server_id=server.id,
            code="abc123",
            created_by=server.owner_id,
            max_uses=None,
            expires_at=None,
        )
    )
    user_id = uuid4()
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=user_id, role=ServerMemberRole.member
        )
    )

    await use_case(user_id=user_id, code=invite.code)

    assert len(members.members) == 1
    assert room_membership_updater.joined == [(user_id, server_room(server.id))]
