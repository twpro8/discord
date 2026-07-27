from functools import cache
from typing import Any

from sqlalchemy import inspect as sa_inspect

from src.platform.database import Base
from src.shared.schemas import BaseSchema


class BaseMapper[OrmModel: Base, Schema: BaseSchema]:
    orm_class: type[OrmModel]
    schema_class: type[Schema]

    @classmethod
    def to_schema(cls, orm_obj: OrmModel) -> Schema:
        """Map ORM model instance to Pydantic schema."""
        return cls.schema_class.model_validate(orm_obj)

    @classmethod
    def to_orm(cls, schema: Schema, **extra: Any) -> OrmModel:
        """Map Pydantic schema to ORM model instance."""
        data = schema.model_dump(exclude_unset=True)
        return cls.orm_class(**data, **extra)

    @classmethod
    def update_orm(cls, orm_obj: OrmModel, schema: Schema) -> OrmModel:
        """Patch an existing ORM instance from a schema."""
        for field, value in schema.model_dump(exclude_unset=True).items():
            if field in cls._valid_keys():
                setattr(orm_obj, field, value)
        return orm_obj

    @classmethod
    @cache
    def _valid_keys(cls) -> set[str]:
        """Return a set of all keys present in cls."""
        return {p.key for p in sa_inspect(cls.orm_class).mapper.iterate_properties}
