import dataclasses
from typing import Any, Final


class _UnsetType:
    """Sentinel marking a field as not explicitly provided.

    Plain dataclasses have no equivalent of Pydantic's `model_fields_set`, so
    partial-update DTOs default optional fields to `UNSET` instead of `None`
    (which would otherwise be indistinguishable from "explicitly set to null").
    """

    _instance: _UnsetType | None = None

    def __new__(cls) -> _UnsetType:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self) -> bool:
        return False


UNSET: Final = _UnsetType()

type Unsettable[T] = T | _UnsetType


def set_fields(data: Any) -> dict[str, Any]:
    """Returns only the fields of a dataclass that were not left as `UNSET`.

    Replaces Pydantic's `model_dump(exclude_unset=True)` for partial-update DTOs.
    """
    return {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
