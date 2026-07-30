from fastapi import APIRouter

from src.modules.friends.transport.http.router import router as friends_http_router


def register_friends_module() -> APIRouter:
    return friends_http_router
