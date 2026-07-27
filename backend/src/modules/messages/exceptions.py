from src.common.errors import LumiereError, NotFoundError


class MessageError(LumiereError): ...


class MessageNotFoundError(MessageError, NotFoundError):
    detail = "Message not found"
