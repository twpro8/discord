from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.infrastructure.persistence.models import ChannelOrm
from src.shared.repositories import BaseMapper


class ChannelMapper(BaseMapper[ChannelOrm, Channel]):
    orm_class = ChannelOrm
    schema_class = Channel
