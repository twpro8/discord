from dataclasses import Field
from typing import Protocol, ClassVar, Any


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]
