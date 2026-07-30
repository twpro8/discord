from fastapi import status

from src.shared.errors import (
    ConflictError,
    LumiereError,
    NotFoundError,
    ValidationError,
)


class UserError(LumiereError): ...


class UserNotFoundError(UserError, NotFoundError):
    detail = "User not found"


class UserAlreadyExistsError(UserError, ConflictError):
    detail = "User already exists"


class IncorrectPasswordError(UserError):
    detail = "Incorrect password"
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidEmail(UserError, ValidationError):
    def __init__(self, value: str) -> None:
        super().__init__(f"'{value}' is not a valid email address")


class InvalidUsername(UserError, ValidationError):
    def __init__(self, value: str) -> None:
        super().__init__(f"'{value}' is not a valid username (3-32 characters)")
