"""
Aggregates all ORM models into a single module.

This module ensures that all model classes are imported and registered
in SQLAlchemy's metadata. It is primarily used by Alembic during
autogeneration, so that all tables are discovered correctly.

Do not remove or bypass these imports unless you update Alembic's
model discovery logic accordingly.
"""

from src.auth.models import RefreshTokenOrm
from src.channel.models import ChannelOrm
from src.chat.models import ChatOrm
from src.message.models import MessageOrm
from src.server.models import ServerOrm
from src.user.models import UserOrm

__all__ = [
    "UserOrm",
    "ServerOrm",
    "ChannelOrm",
    "ChatOrm",
    "MessageOrm",
    "RefreshTokenOrm",
]
