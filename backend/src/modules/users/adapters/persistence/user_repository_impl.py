from sqlalchemy import select

from src.modules.users.adapters.persistence.mappers import UserDataMapper
from src.modules.users.adapters.persistence.models import UserOrm
from src.modules.users.domain.entities.dtos import UserCreate, UserUpdate
from src.modules.users.domain.entities.user import User
from src.shared.adapters.base_repository import BaseRepository


class UserRepositoryImpl(BaseRepository[UserOrm, User, UserCreate, UserUpdate]):
    _model = UserOrm
    _mapper = UserDataMapper

    async def get_by_username(self, username: str) -> User | None:
        query = select(UserOrm).filter_by(username=username)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return UserDataMapper.to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        query = select(UserOrm).filter_by(email=email)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return UserDataMapper.to_entity(model) if model else None
