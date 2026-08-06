from enum import StrEnum


class JobTaskName(StrEnum):
    """Wire-level Celery task name discriminator.

    Values are the literal `name=` strings registered on `@celery_app.task`
    and passed to `JobDispatcher.enqueue` — kept in one place, mirroring
    `core.realtime.envelope.EventType`, so mypy catches a typo at the call
    site instead of it silently creating a dispatch nobody handles.
    """

    PING = "core.ping"
