from fastapi import APIRouter

from src.user.router import router as user_router
from src.auth.router import router as auth_router
from src.chat.router import router as chat_router
from src.server.router import router as server_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(chat_router)
api_router.include_router(server_router)
