from typing import Any, Protocol

from src.shared.application.command import Command
from src.shared.application.query import Query


class Mediator(Protocol):
    """Abstract mediator contract.

    Domain/application/presentation code depends on this Protocol only.
    The concrete implementation is
    shared.application.in_process_mediator.InProcessMediator, built fresh
    per request by api/v1/dependencies.py::get_mediator. Handlers are
    resolved lazily, per dispatch, from a process-lifetime HandlerRegistry
    (shared/application/handler_registry.py, built once by
    composition/handlers.py::build_handler_registry) against this
    request's own RequestServices -- so a fresh Mediator instance per
    request is still required for session isolation, even though the
    registry mapping itself is shared across requests.
    """

    async def send(self, command: Command) -> Any: ...

    async def query(self, query: Query) -> Any: ...
