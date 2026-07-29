from src.shared.schemas import BaseSchema


class UserCreate(BaseSchema):
    name: str
    username: str
    email: str
    password_hash: str
