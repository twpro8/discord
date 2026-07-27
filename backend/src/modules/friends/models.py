"""SQLAlchemy models for friend relationships."""

# Python modules
from typing import TYPE_CHECKING
from uuid import UUID

# Third-party modules
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Project modules
from src.core.database import UUIDBase, timestamp
from src.modules.friends.enums import FriendStatus

if TYPE_CHECKING:
    from src.modules.users.infrastructure.persistence.models import UserOrm


class FriendOrm(UUIDBase):
    """A directed friend request or relationship between two users."""

    __tablename__ = "friends"
    __table_args__ = (
        CheckConstraint("user_id <> target_user_id", name="ck_friends_distinct_users"),
        UniqueConstraint("user_id", "target_user_id", name="uq_friends_user_target"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[FriendStatus] = mapped_column(
        SqlEnum(FriendStatus, name="friend_status"),
        nullable=False,
        default=FriendStatus.PENDING,
    )
    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    user: Mapped[UserOrm] = relationship(
        foreign_keys=[user_id],
        back_populates="sent_relationships",
    )
    target_user: Mapped[UserOrm] = relationship(
        foreign_keys=[target_user_id],
        back_populates="received_relationships",
    )
