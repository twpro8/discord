from uuid import uuid4

from src.core.realtime.rooms import server_room
from src.modules.servers.application.commands.join_server import (
    JoinServerCommand,
    JoinServerCommandHandler,
)
from src.modules.servers.domain.entities.dtos import (
    ServerCreate,
    ServerInviteCreate,
    ServerMemberCreate,
)
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import ServerInviteNotFoundError
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
    handler = JoinServerCommandHandler(uow, FakeRoomMembershipUpdater())

    result = await handler.handle(JoinServerCommand(user_id=uuid4(), code="nope"))

    assert result.is_err
    assert isinstance(result.error, ServerInviteNotFoundError)


async def test_joins_server_and_joins_room() -> None:
    servers = FakeServerRepository()
    members = FakeServerMemberRepository()
    invites = FakeServerInviteRepository()
    uow = FakeServerUnitOfWork(servers, members, invites)
    room_membership_updater = FakeRoomMembershipUpdater()
    handler = JoinServerCommandHandler(uow, room_membership_updater)

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

    result = await handler.handle(JoinServerCommand(user_id=user_id, code=invite.code))

    assert result.is_ok
    assert result.value.user_id == user_id
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
    handler = JoinServerCommandHandler(uow, room_membership_updater)

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

    result = await handler.handle(JoinServerCommand(user_id=user_id, code=invite.code))

    assert result.is_ok
    assert len(members.members) == 1
    assert room_membership_updater.joined == [(user_id, server_room(server.id))]
