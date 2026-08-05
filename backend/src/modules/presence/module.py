from fastapi import APIRouter

from src.modules.presence.transport.http.router import router as presence_http_router


def register_presence_module() -> APIRouter:
    return presence_http_router
