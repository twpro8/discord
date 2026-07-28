from typing import Any


def get_discriminator_value(v: Any) -> str | None:
    if isinstance(v, dict):
        if "chat_id" in v:
            return "chat"
        if "channel_id" in v:
            return "channel"
    else:
        if getattr(v, "chat_id", None) is not None:
            return "chat"
        if getattr(v, "channel_id", None) is not None:
            return "channel"
    return None
