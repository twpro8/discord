from typing import Any, Protocol

from src.shared.application.command import Command
from src.shared.application.query import Query


class Mediator(Protocol):
    """Abstract mediator contract.

    Domain/application/presentation code depends on this Protocol only.
    The concrete implementation is
    shared.application.in_process_mediator.InProcessMediator, built fresh
    per request by api/v1/dependencies.py::get_mediator (handlers close
    over a request-scoped session/unit of work, so there is no single
    app-wide instance to wire in composition/container.py).
    """

    async def send(self, command: Command) -> Any: ...

    async def query(self, query: Query) -> Any: ...
