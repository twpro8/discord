from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.infrastructure.persistence.models import RefreshTokenOrm


class RefreshTokenDataMapper:
    @staticmethod
    def to_entity(model: RefreshTokenOrm) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            is_revoked=model.is_revoked,
            expires_at=model.expires_at,
            created_at=model.created_at,
        )
