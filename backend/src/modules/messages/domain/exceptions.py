from src.shared.errors import LumiereError, NotFoundError


class MessageError(LumiereError): ...


class MessageNotFoundError(MessageError, NotFoundError):
    detail = "Message not found"


class ChannelNotFoundError(MessageError, NotFoundError):
    """messages' own error for "the channel a message targets doesn't
    exist" — deliberately not channels.domain.exceptions.ChannelNotFoundError,
    since that would mean importing channels' domain layer directly."""

    detail = "Channel not found"
