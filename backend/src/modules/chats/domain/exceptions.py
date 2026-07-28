from fastapi import status

from src.shared.errors.base import LumiereError, NotFoundError


class ChatError(LumiereError): ...


class SelfChatForbiddenError(ChatError):
    detail = "User cannot create a private chat with themselves"
    status_code = status.HTTP_400_BAD_REQUEST


class ChatNotFoundError(ChatError, NotFoundError):
    detail = "Chat not found"


class ChatPermissionError(ChatError):
    detail = "You do not have permissions to perform this action"
    status_code = status.HTTP_403_FORBIDDEN


class NotChatMemberError(ChatPermissionError):
    detail = "User is not a member of this chat"


class NotChatOwnerError(ChatPermissionError):
    detail = "User is not the owner of this chat"
