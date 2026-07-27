from src.common.repositories import BaseMapper
from src.modules.users.models import UserOrm
from src.modules.users.schemas import User


class UserMapper(BaseMapper[UserOrm, User]):
    orm_class = UserOrm
    schema_class = User
