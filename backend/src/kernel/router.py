from fastapi import APIRouter

from src.modules.auth.router import router as auth_router
from src.modules.channels.router import router as channel_router
from src.modules.chats.router import router as chat_router
from src.modules.friends.router import router as friend_router
from src.modules.servers.router import router as server_router
from src.modules.users.router import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(chat_router)
api_router.include_router(server_router)
api_router.include_router(channel_router)
api_router.include_router(friend_router)
