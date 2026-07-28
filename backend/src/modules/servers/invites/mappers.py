from src.modules.servers.infrastructure.persistence.models import ServerInviteOrm
from src.modules.servers.invites.schemas import ServerInvite
from src.shared.repositories import BaseMapper


class ServerInviteMapper(BaseMapper[ServerInviteOrm, ServerInvite]):
    orm_class = ServerInviteOrm
    schema_class = ServerInvite
