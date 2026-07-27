from src.modules.messages.models import MessageOrm
from src.modules.messages.schemas import Message
from src.shared.repositories import BaseMapper


class MessageMapper(BaseMapper[MessageOrm, Message]):
    orm_class = MessageOrm
    schema_class = Message
