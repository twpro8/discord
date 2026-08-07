from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import UUIDBase, str_255, str_1024, timestamp
from src.modules.email.domain.enums import EmailStatus


class EmailMessageOrm(UUIDBase):
    __tablename__ = "email_messages"
    __table_args__ = (
        Index(
            "uq_email_messages_idempotency_key",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
    )

    idempotency_key: Mapped[str_255 | None]
    to: Mapped[str_255]
    template: Mapped[str_255]  # a module-owned catalog key, not a fixed set
    context: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[EmailStatus] = mapped_column(
        SqlEnum(EmailStatus, name="email_status"),
        default=EmailStatus.PENDING,
    )
    attempts: Mapped[int] = mapped_column(default=0, server_default="0")
    error_message: Mapped[str_1024 | None]
    provider_message_id: Mapped[str_255 | None]
    created_at: Mapped[timestamp]
    # Make sure you have added the trigger to the migration.
    updated_at: Mapped[timestamp]
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
