from typing import Any

from src.shared.application.command import Command
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.query import Query


class InProcessMediator:
    """Dispatches commands/queries to handlers built lazily, per dispatch,
    from a static HandlerRegistry (see shared/application/handler_registry.py).

    The registry -- a `type[Command]`/`type[Query]` -> factory map -- is
    built ONCE at app startup (composition/handlers.py::build_handler_registry,
    called from main.py's create_app(), stored on app.state.handler_registry)
    and shared across every request. RequestServices bundles this request's
    own resources (session, event_bus, cache, realtime_notifier). A
    dispatch resolves its factory from the registry and calls it with
    (services, self) to construct just the one handler needed -- so
    per-request session isolation is unaffected even though the mapping
    itself is process-lifetime: nothing about a handler's construction is
    shared across requests, only the knowledge of *how* to build it.

    Passing `self` lets a factory build a same-request facade that itself
    dispatches through this mediator (e.g. MediatorUsersFacade) with no
    ordering hazard, since factories only ever run at dispatch time, after
    the mediator is fully constructed.
    """

    def __init__(self, registry: HandlerRegistry, services: RequestServices) -> None:
        self._registry = registry
        self._services = services

    async def send(self, command: Command) -> Any:
        handler = self._registry.build_command_handler(
            type(command), self._services, self
        )
        if handler is None:
            raise KeyError(type(command))
        return await handler.handle(command)

    async def query(self, query: Query) -> Any:
        handler = self._registry.build_query_handler(type(query), self._services, self)
        if handler is None:
            raise KeyError(type(query))
        return await handler.handle(query)
