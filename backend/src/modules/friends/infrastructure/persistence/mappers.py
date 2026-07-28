"""Mappers for friend persistence models."""

# Project modules
from src.modules.friends.domain.entities.schemas import FriendRequest
from src.modules.friends.infrastructure.persistence.models import FriendOrm
from src.shared.repositories import BaseMapper


class FriendMapper(BaseMapper[FriendOrm, FriendRequest]):
    """Map friend ORM records to API schemas."""

    orm_class = FriendOrm
    schema_class = FriendRequest
