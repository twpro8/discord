from fastapi import status

from src.core.errors import NotFoundError, LumiereError


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


class OwnerCannotLeaveServerError(ServerError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Owner cannot leave to the server"


class CannotKickSelfError(ServerError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User cannot kick self"


class OnlyOwnerCanKickError(ServerError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Only owner can kick"


class YouAreNotOwnerError(ServerError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You are not owner"
