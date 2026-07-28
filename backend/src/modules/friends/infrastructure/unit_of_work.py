from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.friends.domain.repositories.friend_unit_of_work import (
    AbstractFriendUnitOfWork,
)
from src.modules.friends.infrastructure.persistence.repository import FriendRepository
from src.modules.users.infrastructure.persistence.repository import (
    SqlAlchemyUserRepository,
)
from src.shared.unit_of_work import BaseUnitOfWork


class FriendUnitOfWork(BaseUnitOfWork, AbstractFriendUnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        friend_repository: FriendRepository,
        user_repository: SqlAlchemyUserRepository,
    ) -> None:
        super().__init__(session)
        self.friends = friend_repository
        self.users = user_repository

    def _uow_marker(self) -> None: ...
