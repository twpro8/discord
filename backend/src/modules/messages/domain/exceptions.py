from fastapi import status

from src.shared.errors import LumiereError, NotFoundError, ValidationError


class MessageError(LumiereError): ...


class MessageNotFoundError(MessageError, NotFoundError):
    detail = "Message not found"


class ChannelNotFoundError(MessageError, NotFoundError):
    """messages' own error for "the channel a message targets doesn't
    exist" — deliberately not channels.domain.exceptions.ChannelNotFoundError,
    since that would mean importing channels' domain layer directly."""

    detail = "Channel not found"


class NotMessageSenderError(MessageError):
    detail = "User is not the sender of this message"
    status_code = status.HTTP_403_FORBIDDEN


class MessageEditWindowExpiredError(MessageError, ValidationError):
    detail = "Messages can only be edited within 24 hours of sending"


class MessageDeletePermissionError(MessageError):
    detail = "User is neither the sender nor the owner of this conversation"
    status_code = status.HTTP_403_FORBIDDEN
