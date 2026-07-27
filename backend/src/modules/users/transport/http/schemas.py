from pydantic import EmailStr, Field

from src.shared.schemas import BaseSchema


class UserUpdateRequest(BaseSchema):
    name: str | None = Field(None, max_length=64)
    username: str | None = Field(None, min_length=3, max_length=32)
    email: EmailStr | None = Field(None, min_length=3, max_length=32)
