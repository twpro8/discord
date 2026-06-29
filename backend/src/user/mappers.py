from src.core.repositories.base_data_mapper import BaseMapper
from src.user.models import UserOrm
from src.user.schemas import User


class UserMapper(BaseMapper[UserOrm, User]):
    orm_class = UserOrm
    schema_class = User
