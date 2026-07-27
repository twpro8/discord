from src.modules.servers.invites.schemas import ServerInvite
from src.modules.servers.models import ServerInviteOrm
from src.shared.repositories import BaseMapper


class ServerInviteMapper(BaseMapper[ServerInviteOrm, ServerInvite]):
    orm_class = ServerInviteOrm
    schema_class = ServerInvite
