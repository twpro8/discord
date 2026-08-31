# Aggregates all ORM models into a single module for Alembic autogeneration.

from src.modules.auth.adapters.persistence.models import RefreshTokenOrm
from src.modules.channels.adapters.persistence.models import ChannelOrm
from src.modules.chats.adapters.persistence.models import ChatOrm
from src.modules.email.adapters.persistence.models import EmailMessageOrm
from src.modules.friends.adapters.persistence.models import FriendOrm
from src.modules.messages.adapters.persistence.models import MessageOrm
from src.modules.servers.adapters.persistence.models import ServerOrm
from src.modules.users.adapters.persistence.models import UserOrm

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
