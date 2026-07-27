from src.common.errors import ConflictError, LumiereError, NotFoundError


class UserError(LumiereError): ...


class UserNotFoundError(UserError, NotFoundError):
    detail = "User not found"


class UserAlreadyExistsError(UserError, ConflictError):
    detail = "User already exists"
