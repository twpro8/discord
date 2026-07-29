from datetime import datetime
from uuid import UUID

from src.modules.channels.domain.enums import ChannelType
from src.shared.domain.entity import Entity


class Channel(Entity):
    def __init__(
        self,
        id: UUID,
        name: str,
        server_id: UUID,
        type: ChannelType,
        topic: str | None,
        position: int,
        last_sequence: int,
        is_private: bool,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        super().__init__(id)
        self.name = name
        self.server_id = server_id
        self.type = type
        self.topic = topic
        self.position = position
        self.last_sequence = last_sequence
        self.is_private = is_private
        self.created_at = created_at
        self.updated_at = updated_at
