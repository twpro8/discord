from fastapi import status

from src.shared.errors import ConflictError, LumiereError, NotFoundError


class UserError(LumiereError): ...


class UserNotFoundError(UserError, NotFoundError):
    detail = "User not found"


class UserAlreadyExistsError(UserError, ConflictError):
    detail = "User already exists"


class IncorrectPasswordError(UserError):
    detail = "Incorrect password"
    status_code = status.HTTP_401_UNAUTHORIZED
