from src.core.repositories import BaseRepository
from src.server.models import ServerMemberOrm
from src.server.server_member.mappers import ServerMemberMapper
from src.server.server_member.schemas import (
    ServerMemberSchema,
)


class ServerMemberRepository(BaseRepository[ServerMemberOrm, ServerMemberSchema]):
    model = ServerMemberOrm
    schema = ServerMemberSchema
    mapper = ServerMemberMapper
