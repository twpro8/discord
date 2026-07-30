import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class ID:
    """Base class for strongly-typed identifiers.

    Prevents accidentally passing a UserId where a ChannelId is expected —
    both would just be `str`/`UUID` otherwise.

        @dataclass(frozen=True)
        class UserId(ID):
            pass

        UserId(uuid.uuid4()) != ChannelId(uuid.uuid4())  # different types
    """

    value: uuid.UUID

    @classmethod
    def new(cls) -> ID:
        return cls(uuid.uuid4())

    @classmethod
    def from_str(cls, raw: str) -> ID:
        return cls(uuid.UUID(raw))

    def __str__(self) -> str:
        return str(self.value)
