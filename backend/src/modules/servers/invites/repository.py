from uuid import UUID

from sqlalchemy import CursorResult, or_, update

from src.modules.servers.infrastructure.persistence.models import ServerInviteOrm
from src.modules.servers.invites.mappers import ServerInviteMapper
from src.modules.servers.invites.schemas import ServerInvite
from src.shared.repositories import BaseRepository


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
