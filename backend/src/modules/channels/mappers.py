from src.modules.channels.models import ChannelOrm
from src.modules.channels.schemas import ChannelSchema
from src.shared.repositories import BaseMapper


class ChannelMapper(BaseMapper[ChannelOrm, ChannelSchema]):
    orm_class = ChannelOrm
    schema_class = ChannelSchema
