from src.kernel.repositories.base_data_mapper import BaseMapper
from src.modules.server.models import ServerMemberOrm
from src.modules.server.server_member.schemas import ServerMemberSchema


class ServerMemberMapper(BaseMapper[ServerMemberOrm, ServerMemberSchema]):
    orm_class = ServerMemberOrm
    schema_class = ServerMemberSchema
