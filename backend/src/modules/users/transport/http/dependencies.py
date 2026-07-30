from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.api.v1.dependencies import AccessTokenDep
from src.core.security.jwt import decode_access_token
from src.modules.auth.domain.exceptions import InvalidAccessTokenError


def get_current_user_id(access_token: AccessTokenDep) -> UUID:
    user_id = decode_access_token(access_token).get("sub")
    if not user_id:
        raise InvalidAccessTokenError
    return UUID(user_id)


UserIdDep = Annotated[UUID, Depends(get_current_user_id)]
