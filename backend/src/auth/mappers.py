from src.auth.models import RefreshTokenOrm
from src.auth.schemas import RefreshToken
from src.core.repositories.base_data_mapper import BaseMapper


class AuthMapper(BaseMapper[RefreshTokenOrm, RefreshToken]):
    orm_class = RefreshTokenOrm
    schema_class = RefreshToken
