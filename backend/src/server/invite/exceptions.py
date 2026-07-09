from fastapi import status

from src.core.errors.base import LumiereError, NotFoundError


class ServerInviteError(LumiereError):
    detail = "Server Invite Error"


class ServerInvitePermissionDeniedError(ServerInviteError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only the server owner can perform this action."


class ServerInviteGenerationFailedError(ServerInviteError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Failed to generate a unique invite code due to multiple collisions. Please try again."


class ServerInviteNotFoundError(ServerInviteError, NotFoundError):
    detail = "Invite code not found in this server."


class ServerInviteCannotDeleteError(ServerInviteError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only the server owner can delete invites."
