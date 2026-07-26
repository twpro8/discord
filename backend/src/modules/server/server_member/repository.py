from src.kernel.repositories import BaseRepository
from src.modules.server.models import ServerMemberOrm
from src.modules.server.server_member.mappers import ServerMemberMapper
from src.modules.server.server_member.schemas import (
    ServerMemberSchema,
)


class ServerMemberRepository(BaseRepository[ServerMemberOrm, ServerMemberSchema]):
    model = ServerMemberOrm
    schema = ServerMemberSchema
    mapper = ServerMemberMapper
