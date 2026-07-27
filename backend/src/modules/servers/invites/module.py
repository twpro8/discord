from fastapi import APIRouter

from src.modules.servers.invites.router import router as server_invites_http_router


def register_server_invites_module() -> APIRouter:
    return server_invites_http_router
