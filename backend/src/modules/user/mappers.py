from src.kernel.repositories.base_data_mapper import BaseMapper
from src.modules.user.models import UserOrm
from src.modules.user.schemas import User


class UserMapper(BaseMapper[UserOrm, User]):
    orm_class = UserOrm
    schema_class = User
