from src.kernel.repositories.base_data_mapper import BaseMapper
from src.modules.servers.invites.schemas import ServerInvite
from src.modules.servers.models import ServerInviteOrm


class ServerInviteMapper(BaseMapper[ServerInviteOrm, ServerInvite]):
    orm_class = ServerInviteOrm
    schema_class = ServerInvite
