from typing import Any, Protocol

from src.shared.application.command import Command
from src.shared.application.query import Query


class Mediator(Protocol):
    """Abstract mediator contract.

    Domain/application/presentation code depends on this Protocol only.
    The concrete implementation (kernel.mediator.InProcessMediator) is
    wired in composition/container.py — nothing above `kernel` should
    import that concrete class directly.
    """

    async def send(self, command: Command) -> Any: ...

    async def query(self, query: Query) -> Any: ...
