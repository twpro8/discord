from fastapi import APIRouter

from src.user.schemas import UserRead
from src.user.dependencies import CurrentUserDep

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    summary="Get current user",
    response_model=UserRead,
)
async def get_current_user(user: CurrentUserDep) -> UserRead:
    """Get current user"""
    return UserRead.model_validate(user)
