from asyncpg.exceptions import ForeignKeyViolationError
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.modules.messages.domain.entities.schemas import Message
from src.modules.messages.domain.exceptions import MessageNotFoundError
from src.modules.messages.infrastructure.persistence.mappers import MessageMapper
from src.modules.messages.models import MessageOrm
from src.shared.repositories import BaseRepository


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
