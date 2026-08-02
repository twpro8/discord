"""Integration test for channels' registry-driven dispatch.

channels is the pilot module migrated off eager per-request handler
registration (see composition/handlers.py and
shared/application/in_process_mediator.py's docstring): its composition.py
now registers a factory on the process-lifetime HandlerRegistry instead of
an eager instance on the mediator directly.

CreateChannelCommand has no HTTP route dispatching it via the mediator --
the only production caller is HandlerBackedChannelsFacade
(modules/channels/public/facade.py), which deliberately bypasses the
mediator/registry entirely and builds its own handler directly (per that
class's docstring: same-transaction delegation, not a mediator dispatch).
This test is the one place that exercises
mediator.send(CreateChannelCommand(...)) against the real, registry-driven
wiring end-to-end, against a real database.
"""

from typing import Any, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.composition.handlers import build_handler_registry
from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
)
from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.servers.domain.entities.dtos import ServerCreate
from src.modules.servers.infrastructure.persistence.server_repository_impl import (
    ServerRepositoryImpl,
)
from src.shared.application.handler_registry import RequestServices
from src.shared.application.in_process_mediator import InProcessMediator

_SEEDED_USER_ID = UUID("c08386e7-bbab-43b4-8427-d296390a3e1e")


async def test_create_channel_command_dispatches_via_the_registry(
    session: AsyncSession,
) -> None:
    server_repository = ServerRepositoryImpl(session)
    server = await server_repository.create(
        ServerCreate(
            name="Registry Test Server",
            description=None,
            owner_id=_SEEDED_USER_ID,
        )
    )

    registry = build_handler_registry()
    services = RequestServices(
        session=session,
        event_bus=cast(Any, object()),
        cache=cast(Any, object()),
        realtime_notifier=cast(Any, object()),
    )
    mediator = InProcessMediator(registry=registry, services=services)

    result = await mediator.send(
        CreateChannelCommand(server_id=server.id, name="general")
    )

    assert result.is_ok
    channel = result.value
    assert channel.server_id == server.id

    channel_repository = ChannelRepositoryImpl(session)
    persisted = await channel_repository.find_by_id(channel.id)
    assert persisted is not None
    assert persisted.name == "general"
