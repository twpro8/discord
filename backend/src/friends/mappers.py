"""Mappers for friend persistence models."""

# Project modules
from src.core.repositories.base_data_mapper import BaseMapper
from src.friends.models import FriendOrm
from src.friends.schemas import FriendRequest


class FriendMapper(BaseMapper[FriendOrm, FriendRequest]):
    """Map friend ORM records to API schemas."""

    orm_class = FriendOrm
    schema_class = FriendRequest
