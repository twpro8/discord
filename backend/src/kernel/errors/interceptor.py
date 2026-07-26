from fastapi import Request
from fastapi.responses import JSONResponse

from src.kernel.errors.base import LumiereError


async def app_exception_handler(
    _: Request,
    e: LumiereError,
) -> JSONResponse:
    return JSONResponse(
        status_code=e.status_code,
        content={"detail": e.detail},
    )
