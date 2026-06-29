from src.core.errors import LumiereError, NotFoundError, ConflictError


class UserError(LumiereError): ...


class UserNotFoundError(UserError, NotFoundError):
    detail = "User not found"


class UserAlreadyExistsError(UserError, ConflictError):
    detail = "User already exists"
