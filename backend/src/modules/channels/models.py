import uuid

from sqlalchemy import UUID, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import UUIDBase, str_128, str_1024, timestamp
from src.modules.channels.enums import ChannelType


class ChannelOrm(UUIDBase):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint("server_id", "name", name="uq_channels_server_name"),
        Index("ix_channels_server_id", "server_id"),
    )

    server_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("servers.id", ondelete="CASCADE"),
    )
    type: Mapped[str_128] = mapped_column(default=ChannelType.text)  # text/voice etc.
    name: Mapped[str_128]
    topic: Mapped[str_1024 | None]
    position: Mapped[int] = mapped_column(default=0)
    last_sequence: Mapped[int] = mapped_column(default=0, server_default="0")
    is_private: Mapped[bool] = mapped_column(
        default=False,
    )  # Reserved; always False in MVP
    created_at: Mapped[timestamp]
    # Make sure you have added the trigger to the migration.
    updated_at: Mapped[timestamp]
