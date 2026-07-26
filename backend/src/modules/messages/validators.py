from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.modules.messages.schemas import MessageCreate


def validate_target(instance: MessageCreate) -> None:
    if (instance.chat_id is None) == (instance.channel_id is None):
        raise ValueError("Exactly one of 'chat_id' or 'channel_id' must be provided.")
