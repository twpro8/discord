from fastapi import status

from src.core.errors import LumiereError


class AuthorizationError(LumiereError):
    detail = "Authorization error"
    status_code = status.HTTP_401_UNAUTHORIZED


class IncorrectPasswordError(AuthorizationError):
    detail = "Incorrect password"


class InvalidAccessTokenError(AuthorizationError):
    detail = "Invalid access token"


class InvalidRefreshTokenError(AuthorizationError):
    detail = "Invalid refresh token"


class NoRefreshTokenError(AuthorizationError):
    detail = "No refresh token"
