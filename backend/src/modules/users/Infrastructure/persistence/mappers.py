from src.modules.users.domain.schemas import User
from src.modules.users.Infrastructure.persistence.models import UserOrm
from src.shared.repositories import BaseMapper


class UserMapper(BaseMapper[UserOrm, User]):
    orm_class = UserOrm
    schema_class = User
