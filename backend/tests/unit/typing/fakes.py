from collections.abc import Mapping
from typing import Any

from src.core.realtime.envelope import EventType


class FakeRealtimeNotifier:
    def __init__(self) -> None:
        self.published: list[tuple[str, EventType, Mapping[str, Any]]] = []
        self.raise_for_rooms: set[str] = set()

    async def publish_to_room(
        self, room: str, event_type: EventType, payload: Mapping[str, Any]
    ) -> None:
        if room in self.raise_for_rooms:
            raise RuntimeError("boom")
        self.published.append((room, event_type, dict(payload)))
