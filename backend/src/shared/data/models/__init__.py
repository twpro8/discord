"""
Aggregates all ORM models into a single module.

This module ensures that all model classes are imported and registered
in SQLAlchemy's metadata. It is primarily used by Alembic during
autogeneration, so that all tables are discovered correctly.

Do not remove or bypass these imports unless you update Alembic's
model discovery logic accordingly.
"""

from src.modules.auth.infrastructure.persistence.models import RefreshTokenOrm
from src.modules.channels.infrastructure.persistence.models import ChannelOrm
from src.modules.chats.infrastructure.persistence.models import ChatOrm
from src.modules.email.infrastructure.persistence.models import EmailMessageOrm
from src.modules.friends.infrastructure.persistence.models import FriendOrm
from src.modules.messages.infrastructure.persistence.models import MessageOrm
from src.modules.servers.infrastructure.persistence.models import ServerOrm
from src.modules.users.infrastructure.persistence.models import UserOrm

__all__ = [
    "UserOrm",
    "ServerOrm",
    "ChannelOrm",
    "ChatOrm",
    "MessageOrm",
    "RefreshTokenOrm",
    "FriendOrm",
    "EmailMessageOrm",
]
