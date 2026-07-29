from typing import Protocol

from src.shared.application.command import Command


class CommandHandler[TCommand: Command, TResult](Protocol):
    async def handle(self, command: TCommand) -> TResult: ...
