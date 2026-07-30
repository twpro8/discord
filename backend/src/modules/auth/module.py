from fastapi import APIRouter

from src.modules.auth.transport.http.router import router as auth_http_router


def register_auth_module() -> APIRouter:
    return auth_http_router
