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


class ServerPermissionError(ServerError):
    detail = "You do not have permissions to perform this action"
    status_code = status.HTTP_403_FORBIDDEN


class NotServerMemberError(ServerPermissionError):
    detail = "User is not a member of this server"


class NotServerOwnerError(ServerPermissionError):
    detail = "User is not the owner of this server"


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
