from fastapi import APIRouter

from src.modules.calls.transport.http.router import router as calls_http_router


def register_calls_module() -> APIRouter:
    return calls_http_router
