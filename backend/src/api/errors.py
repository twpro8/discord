from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.common.errors import LumiereError
from src.kernel.logging import get_logger

logger = get_logger(__name__)


def _problem_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LumiereError)
    async def handle_app_error(_: Request, e: LumiereError) -> JSONResponse:
        return _problem_response(e.status_code, e.detail)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, _: Exception) -> JSONResponse:
        logger.error("unhandled_exception", path=str(request.url))
        return _problem_response(500, "Internal server error")
