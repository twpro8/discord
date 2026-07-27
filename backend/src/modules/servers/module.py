from fastapi import APIRouter

from src.modules.servers.router import router as servers_http_router


def register_servers_module() -> APIRouter:
    return servers_http_router
