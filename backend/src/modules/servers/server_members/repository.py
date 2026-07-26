from src.kernel.repositories import BaseRepository
from src.modules.servers.models import ServerMemberOrm
from src.modules.servers.server_members.mappers import ServerMemberMapper
from src.modules.servers.server_members.schemas import (
    ServerMemberSchema,
)


class ServerMemberRepository(BaseRepository[ServerMemberOrm, ServerMemberSchema]):
    model = ServerMemberOrm
    schema = ServerMemberSchema
    mapper = ServerMemberMapper
