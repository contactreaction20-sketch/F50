"""Security and audit logging interface stubs.

These stubs keep the local security architecture explicit and extensible.
"""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AuditRecord:
    event: str
    timestamp: str
    level: str = "INFO"
    action: str = ""
    permission: str = ""


@dataclass
class AuditEvent:
    event: str
    timestamp: str
    level: str = "INFO"


class AuditLog:
    """Simple append-only local audit log."""

    def __init__(self):
        self.events: list[AuditRecord] = []

    def record(self, event: str, level: str = "INFO", permission: str = "", action: str = "") -> AuditRecord:
        item = AuditRecord(
            event=event,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            action=action,
            permission=permission,
        )
        self.events.append(item)
        return item
