from src.modules.auth.domain.entities.refresh_token import RefreshToken
from src.modules.auth.infrastructure.persistence.models import RefreshTokenOrm
from src.shared.repositories import BaseMapper


class AuthMapper(BaseMapper[RefreshTokenOrm, RefreshToken]):
    orm_class = RefreshTokenOrm
    schema_class = RefreshToken
