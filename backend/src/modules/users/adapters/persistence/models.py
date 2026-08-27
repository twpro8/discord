from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import UUIDBase, str_128, str_255, str_512, timestamp

if TYPE_CHECKING:
    from src.modules.auth.adapters.persistence.models import RefreshTokenOrm
    from src.modules.friends.adapters.persistence.models import FriendOrm


class UserOrm(UUIDBase):
    __tablename__ = "users"

    name: Mapped[str_128]
    username: Mapped[str_128] = mapped_column(unique=True)
    email: Mapped[str_128] = mapped_column(unique=True)
    password_hash: Mapped[str_255]
    avatar_url: Mapped[str_512 | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    refresh_tokens: Mapped[list[RefreshTokenOrm]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    sent_relationships: Mapped[list[FriendOrm]] = relationship(
        foreign_keys="FriendOrm.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    received_relationships: Mapped[list[FriendOrm]] = relationship(
        foreign_keys="FriendOrm.target_user_id",
        back_populates="target_user",
        cascade="all, delete-orphan",
    )
