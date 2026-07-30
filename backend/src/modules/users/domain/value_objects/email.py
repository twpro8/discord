import re
from dataclasses import dataclass

from src.modules.users.domain.exceptions import InvalidEmail
from src.shared.domain.value_object import ValueObject

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise InvalidEmail(normalized)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
