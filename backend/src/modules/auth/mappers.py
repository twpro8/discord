from src.modules.auth.models import RefreshTokenOrm
from src.modules.auth.schemas import RefreshToken
from src.shared.repositories import BaseMapper


class AuthMapper(BaseMapper[RefreshTokenOrm, RefreshToken]):
    orm_class = RefreshTokenOrm
    schema_class = RefreshToken
