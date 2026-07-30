from fastapi import APIRouter

from src.composition.container import Container


def build_api_v1_router(container: Container) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    for module_router in container.module_routers:
        router.include_router(module_router)

    return router
