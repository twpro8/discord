from src.shared.errors import (
    ConflictError,
    LumiereError,
    NotFoundError,
    ValidationError,
)


class ChannelError(LumiereError): ...


class ChannelNotFoundError(ChannelError, NotFoundError):
    detail = "Channel not found"


class ChannelConflictError(ChannelError, ConflictError):
    detail = "A channel with this name already exists in this server"


class OnlyChannelDeletionError(ChannelError, ValidationError):
    detail = "Cannot delete the only channel in the server"
