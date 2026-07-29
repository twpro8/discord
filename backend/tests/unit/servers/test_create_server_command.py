from uuid import uuid4

from src.modules.servers.application.commands.create_server import (
    CreateServerCommand,
    CreateServerCommandHandler,
)
from src.modules.servers.domain.entities.server import ServerCreateRequest
from src.modules.servers.domain.enums import ServerMemberRole
from tests.unit.servers.fakes import (
    FakeCreateChannelCommandHandler,
    FakeServerInviteRepository,
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServerUnitOfWork,
)


async def test_creates_server_owner_membership_and_default_channel() -> None:
    servers = FakeServerRepository()
    members = FakeServerMemberRepository()
    uow = FakeServerUnitOfWork(servers, members, FakeServerInviteRepository())
    create_channel_command = FakeCreateChannelCommandHandler()
    handler = CreateServerCommandHandler(uow, create_channel_command)  # type: ignore[arg-type]
    owner_id = uuid4()

    result = await handler.handle(
        CreateServerCommand(
            server_data=ServerCreateRequest(name="My Server", description="desc"),
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

    assert create_channel_command.calls == [(server.id, "general")]
    assert uow.committed
