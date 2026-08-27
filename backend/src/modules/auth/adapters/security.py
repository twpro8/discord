import hashlib
import secrets


def create_refresh_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(48)
    token_hash = hash_refresh_token(token)
    return token, token_hash


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
