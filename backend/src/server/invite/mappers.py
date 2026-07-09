from src.core.repositories.base_data_mapper import BaseMapper
from src.server.invite.schemas import ServerInviteSchema
from src.server.models import ServerInviteOrm


class ServerInviteMapper(BaseMapper[ServerInviteOrm, ServerInviteSchema]):
    orm_class = ServerInviteOrm
    schema_class = ServerInviteSchema
