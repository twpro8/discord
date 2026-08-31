from src.modules.users.adapters.persistence.models import UserOrm
from src.modules.users.domain.entities.user import User
from src.shared.adapters.data_mapper import DataMapper


class UserDataMapper(DataMapper[UserOrm, User]):
    @staticmethod
    def to_entity(model: UserOrm) -> User:
        return User(
            id=model.id,
            name=model.name,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            avatar_url=model.avatar_url,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
