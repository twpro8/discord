"""Mappers for friend persistence models."""

# Project modules
from src.core.repositories.base_data_mapper import BaseMapper
from src.modules.friend.models import FriendOrm
from src.modules.friend.schemas import FriendRequest


class FriendMapper(BaseMapper[FriendOrm, FriendRequest]):
    """Map friend ORM records to API schemas."""

    orm_class = FriendOrm
    schema_class = FriendRequest
