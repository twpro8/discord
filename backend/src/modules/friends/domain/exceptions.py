from fastapi import status

from src.shared.errors import ConflictError, LumiereError, NotFoundError


class FriendError(LumiereError): ...


class CannotSendFriendRequestToSelfError(FriendError):
    detail = "You cannot send a friend request to yourself"
    status_code = status.HTTP_400_BAD_REQUEST


class FriendRequestAlreadyExistsError(FriendError, ConflictError):
    detail = "A friend request or relationship already exists for these users"
    status_code = status.HTTP_409_CONFLICT


class FriendRequestNotFoundError(FriendError, NotFoundError):
    detail = "Friend request not found"
    status_code = status.HTTP_404_NOT_FOUND


class TargetUserNotFoundError(FriendError, NotFoundError):
    """Friends' own error — deliberately not users.domain.exceptions.
    UserNotFoundError, since that would mean importing users' domain layer
    directly instead of going through UsersFacade."""

    detail = "User not found"


class FriendRequestNotPendingError(FriendError):
    detail = "Friend request is not in pending status"
    status_code = status.HTTP_400_BAD_REQUEST


class NotParticipantError(FriendError):
    detail = "You are not a participant in this relationship"
    status_code = status.HTTP_403_FORBIDDEN
