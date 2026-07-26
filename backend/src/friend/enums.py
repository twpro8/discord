"""Enumerations used by the friends domain."""

# Python modules
from enum import StrEnum


class FriendStatus(StrEnum):
    """The lifecycle state of a relationship between two users."""

    PENDING = "PENDING"
    FRIENDS = "FRIENDS"
    BLOCKED = "BLOCKED"
