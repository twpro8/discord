from src.modules.servers.infrastructure.persistence.models import ServerMemberOrm
from src.modules.servers.server_members.mappers import ServerMemberMapper
from src.modules.servers.server_members.schemas import (
    ServerMemberSchema,
)
from src.shared.repositories import BaseRepository


class ServerMemberRepository(BaseRepository[ServerMemberOrm, ServerMemberSchema]):
    model = ServerMemberOrm
    schema = ServerMemberSchema
    mapper = ServerMemberMapper
