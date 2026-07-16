from src.core.repositories.base_data_mapper import BaseMapper
from src.server.invite.schemas import ServerInvite
from src.server.models import ServerInviteOrm


class ServerInviteMapper(BaseMapper[ServerInviteOrm, ServerInvite]):
    orm_class = ServerInviteOrm
    schema_class = ServerInvite
