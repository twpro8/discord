from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.infrastructure.persistence.server_member_repository_impl import (
    ServerMemberRepositoryImpl,
)


def get_server_member_repository(session: SessionDep) -> ServerMemberRepository:
    return ServerMemberRepositoryImpl(session=session)


ServerMemberRepositoryDep = Annotated[
    ServerMemberRepository, Depends(get_server_member_repository)
]
