from src.modules.users.domain.entities.user import User
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
from src.modules.users.infrastructure.persistence.models import UserOrm


class UserDataMapper:
    @staticmethod
    def to_entity(model: UserOrm) -> User:
        return User(
            id=model.id,
            name=model.name,
            username=Username(model.username),
            email=Email(model.email),
            password_hash=model.password_hash,
            avatar_url=model.avatar_url,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(user: User) -> UserOrm:
        # created_at/updated_at deliberately omitted: UserOrm's columns carry a
        # server_default (TIMEZONE('UTC', now())) — the DB clock is the source
        # of truth for these, not the app's. The entity still stamps its own
        # in-memory value (see User.register) for the immediate response, but
        # that value is never written here.
        return UserOrm(
            id=user.id,
            name=user.name,
            username=str(user.username),
            email=str(user.email),
            password_hash=user.password_hash,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
        )
