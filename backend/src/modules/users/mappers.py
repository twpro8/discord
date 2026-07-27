from src.modules.users.models import UserOrm
from src.modules.users.schemas import User
from src.shared.repositories import BaseMapper


class UserMapper(BaseMapper[UserOrm, User]):
    orm_class = UserOrm
    schema_class = User
