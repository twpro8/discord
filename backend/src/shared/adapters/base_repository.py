from dataclasses import asdict
from uuid import UUID

from sqlalchemy import Executable, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.base import UUIDBase
from src.shared.adapters.data_mapper import DataMapper
from src.shared.domain.unset import set_fields
from src.shared.errors import NotFoundError
from src.shared.typing.dataclasses import DataclassInstance


class BaseRepository[
    ModelT: UUIDBase,
    EntityT: object,
    CreateT: DataclassInstance,
    UpdateT: DataclassInstance | None,
]:
    """Provide common CRUD operations for a repository.

    Type parameters:
        ModelT: SQLAlchemy ORM model type.
        EntityT: Domain entity type.
        CreateT: Data type used to create an entity.
        UpdateT: Data type used to update an entity.

    Subclasses are responsible for defining the ORM model and entity mapper.
    Domain-specific queries should be implemented in the respective subclass.
    """

    _session: AsyncSession
    _model: type[ModelT]
    _mapper: type[DataMapper[ModelT, EntityT]]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> EntityT | None:
        query = select(self._model).where(self._model.id == entity_id)
        return await self._execute_and_map_one_or_none(query)

    async def create(self, data: CreateT) -> EntityT:
        stmt = insert(self._model).values(**asdict(data)).returning(self._model)
        return await self._execute_and_map_one(stmt)

    async def update(self, entity_id: UUID, data: UpdateT) -> EntityT:
        stmt = (
            update(self._model)
            .where(self._model.id == entity_id)
            .values(set_fields(data))
            .returning(self._model)
        )
        return await self._execute_and_map_one(stmt)

    async def delete(self, entity_id: UUID) -> None:
        stmt = delete(self._model).where(self._model.id == entity_id)
        await self._session.execute(stmt)

    async def _execute_and_map_one(self, query: Executable) -> EntityT:
        entity = await self._execute_and_map_one_or_none(query)
        if entity is None:
            raise NotFoundError
        return entity

    async def _execute_and_map_one_or_none(self, query: Executable) -> EntityT | None:
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return self._mapper.to_entity(model) if model else None

    async def _execute_and_map_all(self, query: Executable) -> list[EntityT]:
        result = await self._session.execute(query)
        return [self._mapper.to_entity(model) for model in result.scalars().all()]
