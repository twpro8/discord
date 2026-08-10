from src.shared.schemas import BaseSchema


class IceServerResponse(BaseSchema):
    urls: str
    username: str | None = None
    credential: str | None = None


class TurnCredentialsResponse(BaseSchema):
    ice_servers: list[IceServerResponse]
