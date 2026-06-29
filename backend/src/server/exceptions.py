from src.core.errors import NotFoundError, LumiereError


class ServerError(LumiereError):
    detail = "Unknown server error"


class ServerNotEmptyError(ServerError):
    detail = "Cannot delete a server that is not empty"


class ServerNotFoundError(ServerError, NotFoundError):
    detail = "Server not found"


class MemberNotFoundError(ServerError, NotFoundError):
    detail = "Member not found"


class OwnerCannotLeaveServerError(ServerError):
    detail = "Owner cannot leave to the server"


class CannotKickSelfError(ServerError):
    detail = "User cannot kick self"


class OnlyOwnerCanKickError(ServerError):
    detail = "Only owner can kick"
