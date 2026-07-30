from dataclasses import dataclass

from src.modules.users.domain.exceptions import InvalidUsername
from src.shared.domain.value_object import ValueObject

_MIN_LEN = 3
_MAX_LEN = 32


@dataclass(frozen=True)
class Username(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not (_MIN_LEN <= len(normalized) <= _MAX_LEN):
            raise InvalidUsername(normalized)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
