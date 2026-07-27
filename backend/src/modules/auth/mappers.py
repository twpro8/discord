from src.common.repositories import BaseMapper
from src.modules.auth.models import RefreshTokenOrm
from src.modules.auth.schemas import RefreshToken


class AuthMapper(BaseMapper[RefreshTokenOrm, RefreshToken]):
    orm_class = RefreshTokenOrm
    schema_class = RefreshToken
