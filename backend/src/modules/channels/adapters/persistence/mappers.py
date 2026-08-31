from typing import cast

from src.modules.channels.adapters.persistence.models import ChannelOrm
from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.enums import ChannelType
from src.shared.adapters.data_mapper import DataMapper


class ChannelDataMapper(DataMapper[ChannelOrm, Channel]):
    @staticmethod
    def to_entity(model: ChannelOrm) -> Channel:
        return Channel(
            id=model.id,
            name=model.name,
            server_id=model.server_id,
            type=cast(ChannelType, model.type),
            topic=model.topic,
            position=model.position,
            last_sequence=model.last_sequence,
            is_private=model.is_private,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
