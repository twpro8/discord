from abc import ABC, abstractmethod

from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository


class AbstractServerUnitOfWork(ABC):
    servers: ServerRepository
    server_members: ServerMemberRepository
    invites: ServerInviteRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
