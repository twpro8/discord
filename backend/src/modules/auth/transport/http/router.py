from fastapi import APIRouter, status
from fastapi.requests import Request
from fastapi.responses import Response

from src.api.v1.dependencies import MediatorDep
from src.modules.auth.application.commands.login import LoginCommand
from src.modules.auth.application.commands.logout import LogoutCommand
from src.modules.auth.application.commands.refresh import RefreshCommand
from src.modules.auth.application.commands.register import RegisterCommand
from src.modules.auth.domain.entities.schemas import LoginForm, RegisterForm
from src.modules.auth.transport.http.dependencies import (
    OptionalRefreshTokenDep,
    RefreshTokenDep,
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
    mediator: MediatorDep,
    response: Response,
) -> SuccessResponse:
    result = await mediator.send(
        LoginCommand(username=form_data.username, password=form_data.password)
    )
    if result.is_err:
        raise result.error
    tokens = result.value
    set_token_cookies(response, tokens.access_token, tokens.refresh_token)
    return SuccessResponse()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    form_data: RegisterForm,
    mediator: MediatorDep,
    request: Request,
    response: Response,
) -> UserResponse:
    result = await mediator.send(RegisterCommand(form_data=form_data))
    if result.is_err:
        raise result.error
    user = result.value
    response.headers["location"] = f"{request.url.path}/{user.id}"
    return UserResponse.model_validate(user)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    refresh_token: RefreshTokenDep,
    mediator: MediatorDep,
    response: Response,
) -> SuccessResponse:
    result = await mediator.send(RefreshCommand(refresh_token=refresh_token))
    if result.is_err:
        raise result.error
    tokens = result.value
    set_token_cookies(response, tokens.access_token, tokens.refresh_token)
    return SuccessResponse()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: OptionalRefreshTokenDep,
    mediator: MediatorDep,
    response: Response,
) -> None:
    delete_token_cookies(response)
    if refresh_token is None:
        return
    result = await mediator.send(LogoutCommand(refresh_token=refresh_token))
    if result.is_err:
        raise result.error
