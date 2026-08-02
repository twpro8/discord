from fastapi import APIRouter

from src.modules.chats.transport.http.router import router as chats_http_router


def register_chats_module() -> APIRouter:
    return chats_http_router
