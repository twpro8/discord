from fastapi import APIRouter

from src.modules.messages.transport.http.router import (
    channel_message_router,
    chat_message_router,
)

# messages deliberately has no register_messages_module()/top-level router,
# unlike the other 6 modules: its HTTP surface is a sub-resource of chats/
# channels (POST /chats/{chat_id}/messages, /channels/{channel_id}/messages),
# so composition/container.py never mounts it directly — chats' and
# channels' own routers pull these in via router.include_router(...,
# prefix="/{chat_id}" | "/{channel_id}"). Use-case DI wiring is unaffected:
# messages/transport/http/dependencies.py builds its own use cases the same
# way every other module does.


def get_chat_message_router() -> APIRouter:
    return chat_message_router


def get_channel_message_router() -> APIRouter:
    return channel_message_router
