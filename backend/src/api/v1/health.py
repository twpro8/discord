from fastapi import APIRouter
from pydantic import BaseModel

from src.core.version import get_app_version

router = APIRouter(tags=["Meta"])


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version=get_app_version())
