from uuid import uuid4

from src.modules.servers.application.commands.transfer_ownership import (
    TransferServerOwnershipCommand,
    TransferServerOwnershipCommandHandler,
)
from src.modules.servers.domain.entities.server import ServerCreate, UpdateOwnerID
from src.modules.servers.domain.entities.server_member import ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import (
    CannotTransferToSelfError,
    MemberNotFoundError,
    ServerNotFoundError,
    YouAreNotOwnerError,
)
from tests.unit.servers.fakes import (
    FakeServerInviteRepository,
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServerUnitOfWork,
)


def _seeded_uow() -> tuple[
    FakeServerUnitOfWork, FakeServerRepository, FakeServerMemberRepository
]:
    servers = FakeServerRepository()
    members = FakeServerMemberRepository()
    uow = FakeServerUnitOfWork(servers, members, FakeServerInviteRepository())
    return uow, servers, members


async def test_rejects_unknown_server() -> None:
    uow, _, _ = _seeded_uow()
    handler = TransferServerOwnershipCommandHandler(uow)

    result = await handler.handle(
        TransferServerOwnershipCommand(
            server_id=uuid4(),
            current_user_id=uuid4(),
            data=UpdateOwnerID(owner_id=uuid4()),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ServerNotFoundError)


async def test_rejects_transfer_to_self() -> None:
    uow, servers, members = _seeded_uow()
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    handler = TransferServerOwnershipCommandHandler(uow)

    result = await handler.handle(
        TransferServerOwnershipCommand(
            server_id=server.id,
            current_user_id=owner_id,
            data=UpdateOwnerID(owner_id=owner_id),
        )
    )

    assert result.is_err
    assert isinstance(result.error, CannotTransferToSelfError)


async def test_rejects_non_owner() -> None:
    uow, servers, members = _seeded_uow()
    owner_id, member_id, other_id = uuid4(), uuid4(), uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=member_id, role=ServerMemberRole.member
        )
    )
    handler = TransferServerOwnershipCommandHandler(uow)

    result = await handler.handle(
        TransferServerOwnershipCommand(
            server_id=server.id,
            current_user_id=member_id,
            data=UpdateOwnerID(owner_id=other_id),
        )
    )

    assert result.is_err
    assert isinstance(result.error, YouAreNotOwnerError)


async def test_rejects_unknown_new_owner() -> None:
    uow, servers, members = _seeded_uow()
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    handler = TransferServerOwnershipCommandHandler(uow)

    result = await handler.handle(
        TransferServerOwnershipCommand(
            server_id=server.id,
            current_user_id=owner_id,
            data=UpdateOwnerID(owner_id=uuid4()),
        )
    )

    assert result.is_err
    assert isinstance(result.error, MemberNotFoundError)


async def test_transfers_ownership_and_swaps_roles() -> None:
    uow, servers, members = _seeded_uow()
    owner_id, new_owner_id = uuid4(), uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=new_owner_id, role=ServerMemberRole.member
        )
    )
    handler = TransferServerOwnershipCommandHandler(uow)

    result = await handler.handle(
        TransferServerOwnershipCommand(
            server_id=server.id,
            current_user_id=owner_id,
            data=UpdateOwnerID(owner_id=new_owner_id),
        )
    )

    assert result.is_ok
    assert result.value.owner_id == new_owner_id

    roles = {m.user_id: m.role for m in members.members.values()}
    assert roles[owner_id] == ServerMemberRole.member
    assert roles[new_owner_id] == ServerMemberRole.owner
