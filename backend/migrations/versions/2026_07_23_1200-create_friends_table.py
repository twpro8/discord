"""create friends table

Revision ID: create_friends_table
Revises: 271fad0fa4be
Create Date: 2026-07-23 12:00:00.000000
"""

# Python modules
from collections.abc import Sequence

# Third-party modules
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "create_friends_table"
down_revision: str | None = "271fad0fa4be"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the table used to store directed friend relationships."""
    friend_status = sa.Enum("PENDING", "FRIENDS", "BLOCKED", name="friend_status")

    op.create_table(
        "friends",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("target_user_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            friend_status,
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
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
        sa.CheckConstraint(
            "user_id <> target_user_id", name="ck_friends_distinct_users"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "target_user_id", name="uq_friends_user_target"),
    )
    op.execute(
        sa.text(
            """
            CREATE TRIGGER update_friends_updated_at
            BEFORE UPDATE ON friends
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            """
        )
    )


def downgrade() -> None:
    """Drop the table and enum used for friend relationships."""
    op.execute("DROP TRIGGER IF EXISTS update_friends_updated_at ON friends;")
    op.drop_table("friends")
    sa.Enum(name="friend_status").drop(op.get_bind(), checkfirst=True)
