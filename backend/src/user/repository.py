from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.core.repositories import BaseRepository
from src.user.exceptions import UserAlreadyExistsError
from src.user.models import UserOrm
from src.user.schemas import User
from src.user.mappers import UserMapper


class UserRepository(BaseRepository[UserOrm, User]):
    model = UserOrm
    mapper = UserMapper

    async def create(self, data: BaseModel) -> User:
        try:
            user = await super().create(data)
        except IntegrityError:
            raise UserAlreadyExistsError
        return user
