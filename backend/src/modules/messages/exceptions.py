from src.kernel.errors import LumiereError, NotFoundError


class MessageError(LumiereError): ...


class MessageNotFoundError(MessageError, NotFoundError):
    detail = "Message not found"
