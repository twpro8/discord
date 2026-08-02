from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
    CreateChannelCommandHandler,
)
from src.modules.channels.infrastructure.channel_unit_of_work_impl import (
    ChannelUnitOfWorkImpl,
)
from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.mediator import Mediator


def _build_create_channel_handler(
    services: RequestServices, _mediator: Mediator
) -> CreateChannelCommandHandler:
    channel_repository = ChannelRepositoryImpl(services.session)
    uow = ChannelUnitOfWorkImpl(
        session=services.session, channel_repository=channel_repository
    )
    return CreateChannelCommandHandler(uow)


def register_channel_handlers(registry: HandlerRegistry) -> None:
    registry.register_command_factory(
        CreateChannelCommand, _build_create_channel_handler
    )
