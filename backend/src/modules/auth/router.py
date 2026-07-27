from fastapi import APIRouter, status
from fastapi.requests import Request
from fastapi.responses import Response

from src.common.schemas import SuccessResponse
from src.modules.auth.dependencies import (
    AuthServiceDep,
    OptionalRefreshTokenDep,
    RefreshTokenDep,
)
from src.modules.auth.schemas import LoginForm, RegisterForm
from src.modules.auth.utils import delete_token_cookies, set_token_cookies
from src.modules.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def authenticate(
    form_data: LoginForm,
    service: AuthServiceDep,
    response: Response,
) -> SuccessResponse:
    result = await service.login(form_data.username, form_data.password)
    set_token_cookies(response, result.access_token, result.refresh_token)
    return SuccessResponse()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    form_data: RegisterForm,
    service: AuthServiceDep,
    request: Request,
    response: Response,
) -> UserRead:
    user = await service.register(form_data)
    response.headers["location"] = f"{request.url.path}/{user.id}"
    return UserRead.model_validate(user)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    refresh_token: RefreshTokenDep,
    service: AuthServiceDep,
    response: Response,
) -> SuccessResponse:
    tokens = await service.refresh(refresh_token)
    set_token_cookies(response, tokens.access_token, tokens.refresh_token)
    return SuccessResponse()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: OptionalRefreshTokenDep,
    service: AuthServiceDep,
    response: Response,
) -> None:
    delete_token_cookies(response)
    if refresh_token is None:
        return
    await service.logout(refresh_token)
