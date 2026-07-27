from src.common.repositories import BaseMapper
from src.modules.messages.models import MessageOrm
from src.modules.messages.schemas import Message


class MessageMapper(BaseMapper[MessageOrm, Message]):
    orm_class = MessageOrm
    schema_class = Message
