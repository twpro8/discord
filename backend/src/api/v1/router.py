from fastapi import APIRouter

from src.api.v1.health import router as health_router
from src.api.v1.ws import router as realtime_ws_router
from src.composition.container import Container


def build_api_v1_router(container: Container) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    router.include_router(health_router)
    router.include_router(realtime_ws_router)
    for module_router in container.module_routers:
        router.include_router(module_router)

    return router
