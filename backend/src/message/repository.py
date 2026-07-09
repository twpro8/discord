from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import ForeignKeyViolationError

from src.core.repositories import BaseRepository
from src.message.exceptions import MessageNotFoundError
from src.message.mappers import MessageMapper
from src.message.models import MessageOrm
from src.message.schemas import Message


class MessageRepository(BaseRepository[MessageOrm, Message]):
    model = MessageOrm
    mapper = MessageMapper

    async def create(self, data: BaseModel) -> Message:
        try:
            message = await super().create(data)
        except IntegrityError as e:
            cause = getattr(e.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, ForeignKeyViolationError):
                match constraint:
                    case "messages_parent_id_fkey":
                        raise MessageNotFoundError
                raise
            raise
        return message
