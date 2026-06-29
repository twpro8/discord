from fastapi import status

from src.core.errors.base import LumiereError


class ChatError(LumiereError): ...


class SelfChatForbiddenError(ChatError):
    detail = "User cannot create a private chat with themselves"
    status_code = status.HTTP_400_BAD_REQUEST
