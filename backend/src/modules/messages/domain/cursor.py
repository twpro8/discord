import base64


def encode_cursor(sequence: int) -> str:
    return base64.urlsafe_b64encode(str(sequence).encode()).decode()


def decode_cursor(cursor: str) -> int:
    return int(base64.urlsafe_b64decode(cursor.encode()).decode())
