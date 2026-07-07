from src.core.errors import LumiereError, NotFoundError


class ChannelError(LumiereError): ...


class ChannelNotFoundError(ChannelError, NotFoundError):
    detail = "Channel not found"
