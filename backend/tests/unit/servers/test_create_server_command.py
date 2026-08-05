from uuid import uuid4

from src.core.realtime.rooms import server_room
from src.modules.servers.application.commands.create_server import (
    CreateServerCommand,
    CreateServerCommandHandler,
)
from src.modules.servers.domain.entities.dtos import ServerCreateData
from src.modules.servers.domain.enums import ServerMemberRole
from tests.unit.servers.fakes import (
    FakeChannelsFacade,
    FakeRoomMembershipUpdater,
    FakeServerInviteRepository,
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServerUnitOfWork,
)


async def test_creates_server_owner_membership_and_default_channel() -> None:
    servers = FakeServerRepository()
    members = FakeServerMemberRepository()
    uow = FakeServerUnitOfWork(servers, members, FakeServerInviteRepository())
    channels_facade = FakeChannelsFacade()
    room_membership_updater = FakeRoomMembershipUpdater()
    handler = CreateServerCommandHandler(uow, channels_facade, room_membership_updater)
    owner_id = uuid4()

    result = await handler.handle(
        CreateServerCommand(
            server_data=ServerCreateData(name="My Server", description="desc"),
            owner_id=owner_id,
        )
    )

    assert result.is_ok
    server = result.value
    assert server.name == "My Server"
    assert server.owner_id == owner_id

    owner_membership = next(iter(members.members.values()))
    assert owner_membership.user_id == owner_id
    assert owner_membership.role == ServerMemberRole.owner

    assert channels_facade.calls == [(server.id, "general")]
    assert uow.committed
    assert room_membership_updater.joined == [(owner_id, server_room(server.id))]
