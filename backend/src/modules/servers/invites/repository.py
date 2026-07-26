from uuid import UUID

from sqlalchemy import CursorResult, or_, update

from src.kernel.repositories.base_repository import BaseRepository
from src.modules.servers.invites.mappers import ServerInviteMapper
from src.modules.servers.invites.schemas import ServerInvite
from src.modules.servers.models import ServerInviteOrm


class ServerInviteRepository(BaseRepository[ServerInviteOrm, ServerInvite]):
    model = ServerInviteOrm
    mapper = ServerInviteMapper

    async def increment_use_count_atomic(
        self, invite_id: UUID, max_uses: int | None
    ) -> int:
        statement = (
            update(self.model)
            .where(
                self.model.id == invite_id,
                or_(self.model.max_uses.is_(None), self.model.use_count < max_uses),
            )
            .values(use_count=self.model.use_count + 1)
        )

        result: CursorResult = await self.session.execute(statement)  # type: ignore
        return int(result.rowcount) if result.rowcount is not None else 0
