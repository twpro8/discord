from src.core.errors import ObjectNotFoundError, AppException


class ServerError(AppException):
    detail = "Unknown server error"


class ServerNotEmptyError(ServerError):
    detail = "Cannot delete a server that is not empty"


class ServerNotFoundError(ServerError, ObjectNotFoundError):
    detail = "Server not found"


class MemberNotFoundError(ServerError, ObjectNotFoundError):
    detail = "Member not found"


class OwnerCannotLeaveServerError(ServerError):
    detail = "Owner cannot leave to the server"


class CannotKickSelfError(ServerError):
    detail = "User cannot kick self"


class OnlyOwnerCanKickError(ServerError):
    detail = "Only owner can kick"
