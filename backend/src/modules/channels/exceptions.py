from src.kernel.errors import LumiereError, NotFoundError


class ChannelError(LumiereError): ...


class ChannelNotFoundError(ChannelError, NotFoundError):
    detail = "Channel not found"
