from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.errors.base import AppException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
        },
    )
