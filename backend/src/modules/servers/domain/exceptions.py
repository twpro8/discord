from fastapi import status

from src.shared.errors import LumiereError, NotFoundError


class ServerError(LumiereError):
    detail = "Unknown server error"


class ServerNotEmptyError(ServerError):
    detail = "Cannot delete a server that is not empty"


class ServerNotFoundError(ServerError, NotFoundError):
    detail = "Server not found"


class MemberNotFoundError(ServerError, NotFoundError):
    detail = "Member not found"


class CannotTransferToSelfError(ServerError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You cannot transfer to self"


class YouAreNotOwnerError(ServerError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You are not owner"


class ServerInviteError(LumiereError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Server Invite Error"


class ServerInvitePermissionDeniedError(ServerInviteError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only the server owner can perform this action."


class ServerInviteGenerationFailedError(ServerInviteError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Failed to generate a unique invite code due to multiple collisions. Please try again."


class ServerInviteNotFoundError(NotFoundError, ServerInviteError):
    detail = "Invite code not found in this server."


class ServerInviteCannotDeleteError(ServerInviteError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only the server owner can delete invites."
