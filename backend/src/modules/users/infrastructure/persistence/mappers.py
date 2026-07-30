from src.modules.users.domain.entities.user import User
from src.modules.users.infrastructure.persistence.models import UserOrm


def model_to_entity(model: UserOrm) -> User:
    return User(
        id=model.id,
        name=model.name,
        email=model.email,
        username=model.username,
        password_hash=model.password_hash,
        avatar_url=model.avatar_url,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
