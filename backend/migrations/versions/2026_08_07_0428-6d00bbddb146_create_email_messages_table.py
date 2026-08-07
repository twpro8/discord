"""create email_messages table

Revision ID: 6d00bbddb146
Revises: create_friends_table
Create Date: 2026-08-07 04:28:24.948696
"""

# Python modules
from collections.abc import Sequence

# Third-party modules
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6d00bbddb146"
down_revision: str | None = "create_friends_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the email module's delivery ledger table."""
    email_status = sa.Enum("PENDING", "RETRYING", "SENT", "FAILED", name="email_status")

    op.create_table(
        "email_messages",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("to", sa.String(length=255), nullable=False),
        sa.Column("template", sa.String(length=255), nullable=False),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", email_status, nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('UTC', now())"),
            nullable=False,
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_email_messages_idempotency_key",
        "email_messages",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.execute(
        sa.text(
            """
            CREATE TRIGGER update_email_messages_updated_at
            BEFORE UPDATE ON email_messages
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            """
        )
    )


def downgrade() -> None:
    """Drop the email module's delivery ledger table and enum."""
    op.execute(
        "DROP TRIGGER IF EXISTS update_email_messages_updated_at ON email_messages;"
    )
    op.drop_index(
        "uq_email_messages_idempotency_key",
        table_name="email_messages",
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.drop_table("email_messages")
    sa.Enum(name="email_status").drop(op.get_bind(), checkfirst=True)
