from typing import Any

from src.shared.application.command import Command
from src.shared.application.command_handler import CommandHandler
from src.shared.application.query import Query
from src.shared.application.query_handler import QueryHandler


class InProcessMediator:
    """Dispatches commands/queries to handlers registered on this instance.

    Built fresh per request (see api/v1/dependencies.py::get_mediator) since
    handlers close over a request-scoped session/unit of work — there is no
    app-wide singleton registry to keep in sync across requests.
    """

    def __init__(self) -> None:
        self._command_handlers: dict[type[Command], CommandHandler[Any, Any]] = {}
        self._query_handlers: dict[type[Query], QueryHandler[Any, Any]] = {}

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
        return await self._command_handlers[type(command)].handle(command)

    async def query(self, query: Query) -> Any:
        return await self._query_handlers[type(query)].handle(query)
