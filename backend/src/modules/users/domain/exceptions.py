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


class StorageNotConfiguredError(UserError):
    detail = "Object storage is not configured"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class UnsupportedAvatarFormatError(UserError, ValidationError):
    detail = "Avatar must be a JPEG, PNG, or WebP image"
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class AvatarTooLargeError(UserError, ValidationError):
    detail = "Avatar image exceeds the maximum allowed size"
    status_code = status.HTTP_413_CONTENT_TOO_LARGE
