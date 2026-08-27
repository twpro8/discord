from enum import StrEnum


class EmailStatus(StrEnum):
    PENDING = "PENDING"
    RETRYING = "RETRYING"
    SENT = "SENT"
    FAILED = "FAILED"


class EmailTemplateName(StrEnum):
    """The module's own template catalog. Values map 1:1 to a directory
    under `adapters/templates/`. Kept demo-only for now — naming a
    real template after a business flow (e.g. "welcome") is the future
    consuming module's concern once it actually integrates."""

    GENERIC_NOTIFICATION = "generic_notification"
