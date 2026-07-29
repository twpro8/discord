from fastapi import APIRouter, status
from fastapi.requests import Request
from fastapi.responses import Response

from src.modules.auth.domain.entities.schemas import LoginForm, RegisterForm
from src.modules.auth.transport.http.dependencies import (
    LoginCommandDep,
    LogoutCommandDep,
    OptionalRefreshTokenDep,
    RefreshCommandDep,
    RefreshTokenDep,
    RegisterCommandDep,
)
from src.modules.auth.transport.http.utils import (
    delete_token_cookies,
    set_token_cookies,
)
from src.modules.users.transport.http.schemas import UserResponse
from src.shared.schemas import SuccessResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def authenticate(
    form_data: LoginForm,
    command: LoginCommandDep,
    response: Response,
) -> SuccessResponse:
    result = await command(form_data.username, form_data.password)
    set_token_cookies(response, result.access_token, result.refresh_token)
    return SuccessResponse()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    form_data: RegisterForm,
    command: RegisterCommandDep,
    request: Request,
    response: Response,
) -> UserResponse:
    user = await command(form_data)
    response.headers["location"] = f"{request.url.path}/{user.id}"
    return UserResponse.model_validate(user)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    refresh_token: RefreshTokenDep,
    command: RefreshCommandDep,
    response: Response,
) -> SuccessResponse:
    tokens = await command(refresh_token)
    set_token_cookies(response, tokens.access_token, tokens.refresh_token)
    return SuccessResponse()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: OptionalRefreshTokenDep,
    command: LogoutCommandDep,
    response: Response,
) -> None:
    delete_token_cookies(response)
    if refresh_token is None:
        return
    await command(refresh_token)
