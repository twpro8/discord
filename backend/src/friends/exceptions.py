"""Domain errors raised by the friends feature."""

# Third-party modules
from fastapi import status

# Project modules
from src.core.errors import ConflictError, LumiereError


class FriendError(LumiereError):
    """Base error for friend request operations."""


class CannotSendFriendRequestToSelfError(FriendError):
    """Raised when a user attempts to friend themselves."""

    detail = "You cannot send a friend request to yourself"
    status_code = status.HTTP_400_BAD_REQUEST


class FriendRequestAlreadyExistsError(FriendError, ConflictError):
    """Raised when any relationship already exists for a pair of users."""

    detail = "A friend request or relationship already exists for these users"
    status_code = status.HTTP_409_CONFLICT
