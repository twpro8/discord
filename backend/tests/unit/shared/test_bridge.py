from dataclasses import dataclass

from src.shared.domain.unset import UNSET, Unsettable
from src.shared.schemas.base_schema import BaseSchema
from src.shared.schemas.bridge import unsettable_from_request


class _DummyRequest(BaseSchema):
    name: str | None = None
    age: int | None = None


@dataclass(frozen=True, kw_only=True)
class _DummyUpdateData:
    name: Unsettable[str | None] = UNSET
    age: Unsettable[int | None] = UNSET


def test_unsettable_from_request_maps_provided_fields() -> None:
    request = _DummyRequest.model_validate({"name": "alice"})

    data = unsettable_from_request(request, _DummyUpdateData)

    assert data == _DummyUpdateData(name="alice", age=UNSET)


def test_unsettable_from_request_maps_explicit_null_as_set() -> None:
    request = _DummyRequest.model_validate({"name": None, "age": 5})

    data = unsettable_from_request(request, _DummyUpdateData)

    assert data == _DummyUpdateData(name=None, age=5)


def test_unsettable_from_request_all_unset_when_nothing_provided() -> None:
    request = _DummyRequest.model_validate({})

    data = unsettable_from_request(request, _DummyUpdateData)

    assert data == _DummyUpdateData()
