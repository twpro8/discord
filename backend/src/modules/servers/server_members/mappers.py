from src.kernel.repositories.base_data_mapper import BaseMapper
from src.modules.servers.models import ServerMemberOrm
from src.modules.servers.server_members.schemas import ServerMemberSchema


class ServerMemberMapper(BaseMapper[ServerMemberOrm, ServerMemberSchema]):
    orm_class = ServerMemberOrm
    schema_class = ServerMemberSchema
