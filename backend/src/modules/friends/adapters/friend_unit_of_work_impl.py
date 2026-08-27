from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.friends.domain.repositories.friend_repository import FriendRepository
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.shared.data.unit_of_work import BaseUnitOfWork


class FriendUnitOfWorkImpl(BaseUnitOfWork, FriendUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        friend_repository: FriendRepository,
    ) -> None:
        super().__init__(session)
        self.friends = friend_repository

    def _uow_marker(self) -> None: ...
