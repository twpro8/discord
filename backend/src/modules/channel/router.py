from fastapi import APIRouter

from src.modules.message.router import channel_message_router

router = APIRouter(prefix="/channels", tags=["Channels"])
router.include_router(channel_message_router, prefix="/{channel_id}")
