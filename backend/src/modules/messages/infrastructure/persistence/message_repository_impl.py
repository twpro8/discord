from asyncpg.exceptions import ForeignKeyViolationError
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.messages.domain.entities.schemas import Message, MessageCreate
from src.modules.messages.domain.exceptions import MessageNotFoundError
from src.modules.messages.infrastructure.persistence.mappers import model_to_entity
from src.modules.messages.models import MessageOrm


class MessageRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: MessageCreate) -> Message:
        stmt = insert(MessageOrm).values(**data.model_dump()).returning(MessageOrm)
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as e:
            cause = getattr(e.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, ForeignKeyViolationError):
                match constraint:
                    case "messages_parent_id_fkey":
                        raise MessageNotFoundError
                raise
            raise
        return model_to_entity(result.scalar_one())
