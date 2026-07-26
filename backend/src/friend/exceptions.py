"""Domain errors raised by the friends feature."""

# Third-party modules
from fastapi import status

# Project modules
from src.core.errors import ConflictError, LumiereError, NotFoundError


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


class FriendRequestNotFoundError(FriendError, NotFoundError):
    """Raised when a friend request or relationship is not found."""

    detail = "Friend request not found"
    status_code = status.HTTP_404_NOT_FOUND


class FriendRequestNotPendingError(FriendError):
    """Raised when trying to act on a non-pending friend request."""

    detail = "Friend request is not in pending status"
    status_code = status.HTTP_400_BAD_REQUEST


class NotParticipantError(FriendError):
    """Raised when a user tries to act on a relationship they are not part of."""

    detail = "You are not a participant in this relationship"
    status_code = status.HTTP_403_FORBIDDEN
