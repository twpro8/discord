from datetime import datetime
from uuid import UUID

from src.modules.friends.domain.enums import FriendStatus
from src.shared.domain.entity import Entity


class FriendRequest(Entity):
    """A persisted friend request."""

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        target_user_id: UUID,
        status: FriendStatus,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.target_user_id = target_user_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
