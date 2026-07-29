from dataclasses import dataclass
from uuid import uuid4

from src.shared.domain.aggregate_root import AggregateRoot
from src.shared.domain.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class SomethingHappened(DomainEvent):
    payload: str


class DummyAggregate(AggregateRoot):
    def do_something(self, payload: str) -> None:
        self.record_event(SomethingHappened(payload=payload))


def test_pull_events_returns_recorded_events_in_order() -> None:
    aggregate = DummyAggregate(uuid4())

    aggregate.do_something("first")
    aggregate.do_something("second")

    events = aggregate.pull_events()

    assert [e.payload for e in events] == ["first", "second"]  # type: ignore[attr-defined]


def test_pull_events_drains_and_does_not_return_events_twice() -> None:
    aggregate = DummyAggregate(uuid4())
    aggregate.do_something("first")

    first_pull = aggregate.pull_events()
    second_pull = aggregate.pull_events()

    assert len(first_pull) == 1
    assert second_pull == []


def test_aggregate_root_is_still_an_entity() -> None:
    aggregate_id = uuid4()
    aggregate = DummyAggregate(aggregate_id)

    assert aggregate.id == aggregate_id
    assert aggregate == DummyAggregate(aggregate_id)
