from fastapi import status

from src.common.errors import LumiereError


class AuthenticationError(LumiereError):
    detail = "Authorization error"
    status_code = status.HTTP_401_UNAUTHORIZED


class IncorrectPasswordError(AuthenticationError):
    detail = "Incorrect password"


class InvalidAccessTokenError(AuthenticationError):
    detail = "Invalid access token"


class InvalidRefreshTokenError(AuthenticationError):
    detail = "Invalid refresh token"


class NoRefreshTokenError(AuthenticationError):
    detail = "No refresh token"
