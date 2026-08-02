from dataclasses import dataclass
from typing import Any, cast

import pytest

from src.shared.application.command import Command
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
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


def _fake_services() -> RequestServices:
    # RequestServices' fields aren't Protocols (AsyncSession/EventBus/Cache/
    # RealtimeNotifier are concrete third-party or app types) and these
    # tests never touch them -- only that the same instance round-trips
    # through the registry factory matters here.
    return RequestServices(
        session=cast(Any, object()),
        event_bus=cast(Any, object()),
        cache=cast(Any, object()),
        realtime_notifier=cast(Any, object()),
    )


async def test_send_resolves_command_handler_via_registry() -> None:
    registry = HandlerRegistry()
    services = _fake_services()
    seen: dict[str, object] = {}

    def factory(
        passed_services: RequestServices, mediator: object
    ) -> GreetCommandHandler:
        seen["services"] = passed_services
        seen["mediator"] = mediator
        return GreetCommandHandler()

    registry.register_command_factory(GreetCommand, factory)
    mediator = InProcessMediator(registry=registry, services=services)

    result = await mediator.send(GreetCommand(name="chats"))

    assert result == "hello, chats"
    # The factory got this exact request's services and the live mediator
    # instance dispatching it, not stand-ins -- this is what lets a factory
    # build a same-request facade like MediatorUsersFacade(mediator).
    assert seen["services"] is services
    assert seen["mediator"] is mediator


async def test_query_resolves_query_handler_via_registry() -> None:
    registry = HandlerRegistry()
    registry.register_query_factory(
        CountLettersQuery, lambda services, mediator: CountLettersQueryHandler()
    )
    mediator = InProcessMediator(registry=registry, services=_fake_services())

    result = await mediator.query(CountLettersQuery(word="lumiere"))

    assert result == 7


async def test_send_raises_on_unregistered_command_type() -> None:
    mediator = InProcessMediator(registry=HandlerRegistry(), services=_fake_services())

    with pytest.raises(KeyError):
        await mediator.send(GreetCommand(name="chats"))


async def test_query_raises_on_unregistered_query_type() -> None:
    mediator = InProcessMediator(registry=HandlerRegistry(), services=_fake_services())

    with pytest.raises(KeyError):
        await mediator.query(CountLettersQuery(word="lumiere"))
