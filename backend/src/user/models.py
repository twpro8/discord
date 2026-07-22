from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.postgres import UUIDBase, str_128, str_255, str_512, timestamp

if TYPE_CHECKING:
    from src.auth.models import RefreshTokenOrm


class UserOrm(UUIDBase):
    __tablename__ = "users"

    name: Mapped[str_128]
    username: Mapped[str_128] = mapped_column(unique=True)
    email: Mapped[str_128] = mapped_column(unique=True)
    password_hash: Mapped[str_255]
    avatar_url: Mapped[str_512 | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[timestamp]
    # Make sure you have added the trigger to the migration.
    updated_at: Mapped[timestamp]

    refresh_tokens: Mapped[list[RefreshTokenOrm]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
