from typing import Any

from sqlalchemy import Row

from src.core.repositories.base_data_mapper import BaseMapper
from src.server.models import ServerOrm
from src.server.schemas import ServerSchema, ServerUserBriefSchema


class ServerMapper(BaseMapper[ServerOrm, ServerSchema]):
    orm_class = ServerOrm
    schema_class = ServerSchema


class ServerUserBriefMapper(BaseMapper[ServerOrm, ServerUserBriefSchema]):
    orm_class = ServerOrm
    schema_class = ServerUserBriefSchema

    @classmethod
    def to_schema(cls, row: Row[Any] | ServerOrm) -> ServerUserBriefSchema:
        return cls.schema_class.model_validate(row)
