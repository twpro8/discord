from fastapi import APIRouter

from src.modules.messages.module import get_channel_message_router

router = APIRouter(prefix="/channels", tags=["Channels"])
router.include_router(get_channel_message_router(), prefix="/{channel_id}")
