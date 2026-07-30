from dataclasses import dataclass

import pytest

from src.shared.application.command import Command
from src.shared.application.in_process_mediator import InProcessMediator
from src.shared.application.query import Query


@dataclass(frozen=True, kw_only=True)
class GreetCommand(Command):
    name: str


class GreetCommandHandler:
    async def handle(self, command: GreetCommand) -> str:
        return f"hello, {command.name}"


@dataclass(frozen=True, kw_only=True)
class CountLettersQuery(Query):
    word: str


class CountLettersQueryHandler:
    async def handle(self, query: CountLettersQuery) -> int:
        return len(query.word)


async def test_send_dispatches_command_to_its_registered_handler() -> None:
    mediator = InProcessMediator()
    mediator.register_command(GreetCommand, GreetCommandHandler())

    result = await mediator.send(GreetCommand(name="chats"))

    assert result == "hello, chats"


async def test_query_dispatches_query_to_its_registered_handler() -> None:
    mediator = InProcessMediator()
    mediator.register_query(CountLettersQuery, CountLettersQueryHandler())

    result = await mediator.query(CountLettersQuery(word="lumiere"))

    assert result == 7


async def test_send_raises_on_unregistered_command_type() -> None:
    mediator = InProcessMediator()

    with pytest.raises(KeyError):
        await mediator.send(GreetCommand(name="chats"))


async def test_query_raises_on_unregistered_query_type() -> None:
    mediator = InProcessMediator()

    with pytest.raises(KeyError):
        await mediator.query(CountLettersQuery(word="lumiere"))
