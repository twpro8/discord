from pydantic import BaseModel


class SuccessResponse(BaseModel):
    status: str = "OK"
