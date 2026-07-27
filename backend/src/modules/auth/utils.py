from fastapi.responses import Response

from src.platform.config import settings


def set_token_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """Set authentication cookies for access and refresh tokens.

    Args:
        response: FastAPI Response object to attach the cookies to.
        access_token: JWT access token to store in a short-lived cookie.
        refresh_token: JWT refresh token to store in a long-lived cookie.
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def delete_token_cookies(response: Response) -> None:
    """Delete authentication cookies for access and refresh tokens.

    Args:
        response: FastAPI Response object to delete the cookies from.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/api/v1/auth",
    )
