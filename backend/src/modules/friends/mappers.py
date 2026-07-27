"""Mappers for friend persistence models."""

# Project modules
from src.modules.friends.models import FriendOrm
from src.modules.friends.schemas import FriendRequest
from src.shared.repositories import BaseMapper


class FriendMapper(BaseMapper[FriendOrm, FriendRequest]):
    """Map friend ORM records to API schemas."""

    orm_class = FriendOrm
    schema_class = FriendRequest
