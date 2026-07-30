from dataclasses import dataclass

from src.shared.domain.unset import UNSET, Unsettable, set_fields


@dataclass(frozen=True, kw_only=True)
class _DummyUpdate:
    name: Unsettable[str] = UNSET
    age: Unsettable[int] = UNSET


def test_set_fields_omits_unset_fields() -> None:
    data = _DummyUpdate(name="alice")

    assert set_fields(data) == {"name": "alice"}


def test_set_fields_includes_explicitly_set_falsy_values() -> None:
    data = _DummyUpdate(name="alice", age=0)

    assert set_fields(data) == {"name": "alice", "age": 0}


def test_set_fields_returns_empty_dict_when_nothing_set() -> None:
    data = _DummyUpdate()

    assert set_fields(data) == {}


def test_unset_is_falsy_and_a_singleton() -> None:
    assert not UNSET
    assert UNSET is type(UNSET)()
