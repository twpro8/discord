import base64
from datetime import datetime
from uuid import UUID


def encode_cursor(created_at: datetime, chat_id: UUID) -> str:
    raw = f"{created_at.isoformat()}|{chat_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    ts_str, id_str = raw.split("|")
    return datetime.fromisoformat(ts_str), UUID(id_str)
