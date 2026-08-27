from fastapi import APIRouter

from src.api.v1.health import router as health_router
from src.api.v1.ws import router as realtime_ws_router
from src.modules.auth.transport.http.router import router as auth_router
from src.modules.channels.transport.http.router import router as channels_router
from src.modules.chats.transport.http.router import router as chats_router
from src.modules.friends.transport.http.router import router as friends_router
from src.modules.presence.transport.http.router import router as presence_router
from src.modules.servers.transport.http.router import router as servers_router
from src.modules.users.transport.http.router import router as users_router

_MODULE_ROUTERS = [
    auth_router,
    users_router,
    friends_router,
    servers_router,
    channels_router,
    chats_router,
    presence_router,
]


def build_api_v1_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    router.include_router(health_router)
    router.include_router(realtime_ws_router)
    for module_router in _MODULE_ROUTERS:
        router.include_router(module_router)

    return router
