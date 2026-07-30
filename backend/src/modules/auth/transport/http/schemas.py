from pydantic import EmailStr, Field

from src.shared.schemas import BaseSchema


class RegisterForm(BaseSchema):
    name: str = Field(min_length=3, max_length=64)
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr = Field(min_length=3, max_length=32)
    password: str = Field(min_length=3, max_length=128)


class LoginForm(BaseSchema):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=3, max_length=128)
