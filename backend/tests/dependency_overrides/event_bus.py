from src.core.event_bus import EventBus, InMemoryEventBus


def get_test_event_bus() -> EventBus:
    return InMemoryEventBus()
