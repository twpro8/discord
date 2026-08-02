from typing import Any

from src.shared.application.command import Command
from src.shared.application.command_handler import CommandHandler
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.query import Query
from src.shared.application.query_handler import QueryHandler


class InProcessMediator:
    """Dispatches commands/queries to handlers.

    Two dispatch paths coexist while modules migrate off eager registration
    (see shared/application/handler_registry.py):

    - Eager: register_command/register_query attach an already-built
      handler instance directly to this mediator. This is how every module
      still works today (their composition.py is called fresh per request,
      in api/v1/dependencies.py::get_mediator, because those handlers close
      over a request-scoped session/unit of work).
    - Lazy: a HandlerRegistry -- built ONCE at app startup, not per
      request -- maps a command/query type to a factory. On a dispatch miss
      in the eager dict, that factory is called with this request's
      RequestServices and this mediator instance to construct just the one
      handler needed. Only the *mapping* is process-lifetime; the handler
      itself is still built lazily, scoped to the request's own session, so
      per-request isolation is unaffected -- only the eager construction of
      every module's handlers on every request goes away.

    Modules migrate to the lazy path one at a time. Once all have, the
    eager path (register_command/register_query and the two dicts below)
    is removed and this docstring collapses to a single dispatch model.
    """

    def __init__(
        self,
        registry: HandlerRegistry | None = None,
        services: RequestServices | None = None,
    ) -> None:
        self._command_handlers: dict[type[Command], CommandHandler[Any, Any]] = {}
        self._query_handlers: dict[type[Query], QueryHandler[Any, Any]] = {}
        self._registry = registry
        self._services = services

    def register_command(
        self,
        command_type: type[Command],
        handler: CommandHandler[Any, Any],
    ) -> None:
        self._command_handlers[command_type] = handler

    def register_query(
        self,
        query_type: type[Query],
        handler: QueryHandler[Any, Any],
    ) -> None:
        self._query_handlers[query_type] = handler

    async def send(self, command: Command) -> Any:
        handler = self._command_handlers.get(
            type(command)
        ) or self._resolve_command_handler(type(command))
        return await handler.handle(command)

    async def query(self, query: Query) -> Any:
        handler = self._query_handlers.get(type(query)) or self._resolve_query_handler(
            type(query)
        )
        return await handler.handle(query)

    def _resolve_command_handler(
        self, command_type: type[Command]
    ) -> CommandHandler[Any, Any]:
        handler = (
            self._registry.build_command_handler(command_type, self._services, self)
            if self._registry is not None and self._services is not None
            else None
        )
        if handler is None:
            raise KeyError(command_type)
        return handler

    def _resolve_query_handler(self, query_type: type[Query]) -> QueryHandler[Any, Any]:
        handler = (
            self._registry.build_query_handler(query_type, self._services, self)
            if self._registry is not None and self._services is not None
            else None
        )
        if handler is None:
            raise KeyError(query_type)
        return handler
