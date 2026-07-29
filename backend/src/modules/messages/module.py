from fastapi import APIRouter

from src.modules.messages.transport.http.router import (
    channel_message_router,
    chat_message_router,
)


def get_chat_message_router() -> APIRouter:
    return chat_message_router


def get_channel_message_router() -> APIRouter:
    return channel_message_router
