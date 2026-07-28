from src.modules.servers.infrastructure.persistence.models import ServerMemberOrm
from src.modules.servers.server_members.schemas import ServerMemberSchema
from src.shared.repositories import BaseMapper


class ServerMemberMapper(BaseMapper[ServerMemberOrm, ServerMemberSchema]):
    orm_class = ServerMemberOrm
    schema_class = ServerMemberSchema
