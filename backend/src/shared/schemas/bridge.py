import dataclasses
from dataclasses import Field
from typing import Any, ClassVar, Protocol

from pydantic import BaseModel

from src.shared.domain.unset import UNSET


class _IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


def unsettable_from_request[T: _IsDataclass](request: BaseModel, cls: type[T]) -> T:
    """Builds an `Unsettable`-field dataclass from a Pydantic request.

    Uses `request.model_fields_set` to tell which fields the client actually
    sent, mapping the rest to `UNSET` — the inverse of how `*Response.model_validate`
    bridges a domain object out to a transport schema.
    """
    fields_set = request.model_fields_set
    kwargs = {
        f.name: getattr(request, f.name) if f.name in fields_set else UNSET
        for f in dataclasses.fields(cls)
    }
    return cls(**kwargs)
