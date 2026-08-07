import re
from dataclasses import dataclass

from src.modules.email.domain.exceptions import InvalidEmailAddress
from src.shared.domain.value_object import ValueObject

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class EmailAddress(ValueObject):
    """Deliberately not a reuse of `modules.users.domain.value_objects.email.Email`
    — modules never import each other's `domain/`, so this module keeps its
    own copy of the same validation."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise InvalidEmailAddress(normalized)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
