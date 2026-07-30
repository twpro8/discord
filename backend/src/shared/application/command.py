from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Command:
    """Marker base class for write use-cases (CQRS command side).

    Subclass as a frozen dataclass per use case, e.g. RegisterUserCommand.
    Commands carry primitive/plain data only — no ORM models, no domain
    entities — so they stay serializable across a future process boundary.
    """
