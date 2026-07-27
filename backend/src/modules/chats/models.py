import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import UUIDBase, str_128, str_512, timestamp
from src.modules.chats.enums import ChatMemberRole, ChatType


class ChatOrm(UUIDBase):
    __tablename__ = "chats"

    type: Mapped[str_128] = mapped_column(default=ChatType.private)
    name: Mapped[str_128 | None]  # Required for group; NULL for private
    description: Mapped[str_512 | None]
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
    )  # NULL for private chats
    image_url: Mapped[str_512 | None]
    last_sequence: Mapped[int] = mapped_column(default=0, server_default="0")
    is_archived: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[timestamp]
    # Make sure you have added the trigger to the migration.
    updated_at: Mapped[timestamp]


class ChatMemberOrm(UUIDBase):
    __tablename__ = "chat_members"
    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="uq_chat_members_chat_user"),
        Index("ix_chat_members_chat_id", "chat_id"),
        Index("ix_chat_members_user_id", "user_id"),
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
    )
    role: Mapped[str_128] = mapped_column(default=ChatMemberRole.member)
    last_read_seq: Mapped[int] = mapped_column(default=0)
    joined_at: Mapped[timestamp]
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
