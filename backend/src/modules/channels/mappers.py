from src.common.repositories import BaseMapper
from src.modules.channels.models import ChannelOrm
from src.modules.channels.schemas import ChannelSchema


class ChannelMapper(BaseMapper[ChannelOrm, ChannelSchema]):
    orm_class = ChannelOrm
    schema_class = ChannelSchema
