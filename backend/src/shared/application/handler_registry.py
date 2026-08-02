from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import Cache
from src.core.event_bus import EventBus
from src.core.realtime.notifier import RealtimeNotifier
from src.shared.application.command import Command
from src.shared.application.command_handler import CommandHandler
from src.shared.application.mediator import Mediator
from src.shared.application.query import Query
from src.shared.application.query_handler import QueryHandler


@dataclass(frozen=True, kw_only=True)
class RequestServices:
    """Request-scoped resources a lazily-constructed handler factory may
    need. Bundles what get_mediator already builds per request (session,
    event_bus, cache, realtime_notifier) so a HandlerRegistry factory
    closure can build exactly the one handler a dispatch needs, instead of
    every module's handlers being eagerly constructed up front.
    """

    session: AsyncSession
    event_bus: EventBus
    cache: Cache
    realtime_notifier: RealtimeNotifier


CommandHandlerFactory = Callable[[RequestServices, Mediator], CommandHandler[Any, Any]]
QueryHandlerFactory = Callable[[RequestServices, Mediator], QueryHandler[Any, Any]]


class HandlerRegistry:
    """Static, process-lifetime map of command/query type -> handler
    factory.

    Built once at app startup as part of the composition root
    (composition/container.py::build_container(), stored on
    app.state.container.handler_registry) by every module's
    register_<name>_handlers(registry). Each factory is a
    small closure that, given a request's RequestServices and the live
    per-request Mediator instance, constructs ONLY the one handler (and its
    UoW/repositories) a dispatch actually needs -- nothing is built for
    commands/queries that aren't dispatched this request.

    The Mediator argument lets a factory build a same-request facade that
    itself dispatches through the mediator (e.g. MediatorUsersFacade) --
    by the time any factory runs, at dispatch time, the mediator is always
    fully constructed, so this has no ordering hazard.
    """

    def __init__(self) -> None:
        self._command_factories: dict[type[Command], CommandHandlerFactory] = {}
        self._query_factories: dict[type[Query], QueryHandlerFactory] = {}

    def register_command_factory(
        self, command_type: type[Command], factory: CommandHandlerFactory
    ) -> None:
        self._command_factories[command_type] = factory

    def register_query_factory(
        self, query_type: type[Query], factory: QueryHandlerFactory
    ) -> None:
        self._query_factories[query_type] = factory

    def build_command_handler(
        self,
        command_type: type[Command],
        services: RequestServices,
        mediator: Mediator,
    ) -> CommandHandler[Any, Any] | None:
        factory = self._command_factories.get(command_type)
        return factory(services, mediator) if factory else None

    def build_query_handler(
        self,
        query_type: type[Query],
        services: RequestServices,
        mediator: Mediator,
    ) -> QueryHandler[Any, Any] | None:
        factory = self._query_factories.get(query_type)
        return factory(services, mediator) if factory else None
