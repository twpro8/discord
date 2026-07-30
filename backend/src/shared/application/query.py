from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Query:
    """Marker base class for read use-cases (CQRS query side)."""
