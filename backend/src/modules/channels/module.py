from fastapi import APIRouter

from src.modules.channels.router import router as channels_http_router


def register_channels_module() -> APIRouter:
    return channels_http_router
