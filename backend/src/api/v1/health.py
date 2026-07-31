from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Meta"])


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
