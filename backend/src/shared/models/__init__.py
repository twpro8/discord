"""
Aggregates all ORM models into a single module.

This module ensures that all model classes are imported and registered
in SQLAlchemy's metadata. It is primarily used by Alembic during
autogeneration, so that all tables are discovered correctly.

Do not remove or bypass these imports unless you update Alembic's
model discovery logic accordingly.
"""

from src.modules.auth.models import RefreshTokenOrm
from src.modules.channels.models import ChannelOrm
from src.modules.chats.models import ChatOrm
from src.modules.friends.models import FriendOrm
from src.modules.messages.models import MessageOrm
from src.modules.servers.models import ServerOrm
from src.modules.users.Infrastructure.persistence.models import UserOrm

__all__ = [
    "UserOrm",
    "ServerOrm",
    "ChannelOrm",
    "ChatOrm",
    "MessageOrm",
    "RefreshTokenOrm",
    "FriendOrm",
]
