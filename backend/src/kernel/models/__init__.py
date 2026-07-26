"""
Aggregates all ORM models into a single module.

This module ensures that all model classes are imported and registered
in SQLAlchemy's metadata. It is primarily used by Alembic during
autogeneration, so that all tables are discovered correctly.

Do not remove or bypass these imports unless you update Alembic's
model discovery logic accordingly.
"""

from src.modules.auth.models import RefreshTokenOrm
from src.modules.channel.models import ChannelOrm
from src.modules.chat.models import ChatOrm
from src.modules.friend.models import FriendOrm
from src.modules.message.models import MessageOrm
from src.modules.server.models import ServerOrm
from src.modules.user.models import UserOrm

__all__ = [
    "UserOrm",
    "ServerOrm",
    "ChannelOrm",
    "ChatOrm",
    "MessageOrm",
    "RefreshTokenOrm",
    "FriendOrm",
]
