import uuid
from datetime import datetime

from sqlalchemy import UUID, CheckConstraint, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.kernel.database import UUIDBase, timestamp


class MessageOrm(UUIDBase):
    __tablename__ = "messages"
    __table_args__ = (
        # Exactly one context FK must be set — never both, never neither
        CheckConstraint(
            "(chat_id IS NULL) != (channel_id IS NULL)",
            name="ck_messages_single_context",
        ),
        # Sequence uniqueness is scoped per context
        Index(
            "uq_messages_chat_sequence",
            "chat_id",
            "sequence",
            unique=True,
            postgresql_where="chat_id IS NOT NULL",
        ),
        Index(
            "uq_messages_channel_sequence",
            "channel_id",
            "sequence",
            unique=True,
            postgresql_where="channel_id IS NOT NULL",
        ),
    )

    # Context (Option B — dual nullable FKs, exactly one must be set)
    chat_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        index=True,
    )
    channel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id", ondelete="CASCADE"),
        index=True,
    )

    # Authorship
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )

    # Content
    body: Mapped[str | None] = mapped_column(Text)

    # Ordering
    sequence: Mapped[int]

    # Threading
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
    )

    # State flags
    is_edited: Mapped[bool] = mapped_column(default=False)
    is_deleted: Mapped[bool] = mapped_column(default=False)

    # Audit timestamps
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[timestamp]
    # Make sure you have added the trigger to the migration.
    updated_at: Mapped[timestamp]
