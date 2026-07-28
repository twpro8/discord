from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.friends.domain.repositories.friend_repository import FriendRepository
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.shared.unit_of_work import BaseUnitOfWork


class FriendUnitOfWorkImpl(BaseUnitOfWork, FriendUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        friend_repository: FriendRepository,
        user_repository: UserRepository,
    ) -> None:
        super().__init__(session)
        self.friends = friend_repository
        self.users = user_repository

    def _uow_marker(self) -> None: ...
