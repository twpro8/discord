from sqlalchemy.orm import DeclarativeBase

from src.core.database.mixins import UUIDMixin


class Base(DeclarativeBase):
    pass


class UUIDBase(UUIDMixin, Base):
    __abstract__ = True
