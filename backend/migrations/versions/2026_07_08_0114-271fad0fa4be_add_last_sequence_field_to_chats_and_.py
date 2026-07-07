"""add last_sequence field to chats and channels tables

Revision ID: 271fad0fa4be
Revises: 627a46b121a8
Create Date: 2026-07-08 01:14:57.691503

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "271fad0fa4be"
down_revision: Union[str, Sequence[str], None] = "627a46b121a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "channels",
        sa.Column("last_sequence", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "chats",
        sa.Column("last_sequence", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("chats", "last_sequence")
    op.drop_column("channels", "last_sequence")
