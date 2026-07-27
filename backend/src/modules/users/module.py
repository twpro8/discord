from fastapi import APIRouter

from src.modules.users.transport.http.router import router as users_http_router


def register_users_module() -> APIRouter:
    return users_http_router
