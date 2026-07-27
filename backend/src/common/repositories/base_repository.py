from collections.abc import Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Executable

from src.common.errors import NotFoundError
from src.common.repositories.base_data_mapper import BaseMapper
from src.common.schemas.base_schema import BaseSchema
from src.kernel.database import UUIDBase


class BaseRepository[T: UUIDBase, R: BaseSchema]:
    model: type[T]
    schema: type[R]
    mapper: type[BaseMapper[T, R]]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_filtered(
        self,
        limit: int,
        offset: int,
        **filter_by: Any,
    ) -> Sequence[R]:
        query = select(self.model).filter_by(**filter_by).limit(limit).offset(offset)
        return await self._execute_and_map_all(query)

    async def get_one(self, **filter_by: Any) -> R | None:
        query = select(self.model).filter_by(**filter_by)
        return await self._execute_and_map_one_or_none(query)

    async def create(self, data: BaseModel) -> R:
        statement = insert(self.model).values(**data.model_dump()).returning(self.model)
        return await self._execute_and_map_one(statement)

    async def update(
        self,
        id_: UUID,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by: Any,
    ) -> R:
        statement = (
            update(self.model)
            .where(self.model.id == id_)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        return await self._execute_and_map_one(statement)

    async def delete(self, id_: UUID) -> None:
        statement = delete(self.model).where(self.model.id == id_)
        await self.session.execute(statement)

    async def _execute_and_map_one(self, query: Executable) -> R:
        schema = await self._execute_and_map_one_or_none(query)
        if schema is None:
            raise NotFoundError
        return schema

    async def _execute_and_map_one_or_none(self, query: Executable) -> R | None:
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        return self.mapper.to_schema(model) if model else None

    async def _execute_and_map_all(self, query: Executable) -> Sequence[R]:
        result = await self.session.execute(query)
        return [self.mapper.to_schema(model) for model in result.scalars().all()]
