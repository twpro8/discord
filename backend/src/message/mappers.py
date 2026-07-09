from src.core.repositories.base_data_mapper import BaseMapper
from src.message.models import MessageOrm
from src.message.schemas import Message


class MessageMapper(BaseMapper[MessageOrm, Message]):
    orm_class = MessageOrm
    schema_class = Message
