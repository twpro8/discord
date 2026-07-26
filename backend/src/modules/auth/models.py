from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kernel.postgres import UUIDBase, str_128, timestamp

if TYPE_CHECKING:
    from src.modules.user.models import UserOrm


class RefreshTokenOrm(UUIDBase):
    __tablename__ = "refresh_tokens"

    token_hash: Mapped[str_128]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
    )
    is_revoked: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[timestamp]
    created_at: Mapped[timestamp]

    user: Mapped[UserOrm] = relationship(
        back_populates="refresh_tokens",
        lazy="joined",
    )
