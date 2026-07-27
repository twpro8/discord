"""Mappers for friend persistence models."""

# Project modules
from src.common.repositories import BaseMapper
from src.modules.friends.models import FriendOrm
from src.modules.friends.schemas import FriendRequest


class FriendMapper(BaseMapper[FriendOrm, FriendRequest]):
    """Map friend ORM records to API schemas."""

    orm_class = FriendOrm
    schema_class = FriendRequest
