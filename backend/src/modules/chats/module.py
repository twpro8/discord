from fastapi import APIRouter

from src.modules.chats.router import router as chats_http_router


def register_chats_module() -> APIRouter:
    return chats_http_router
