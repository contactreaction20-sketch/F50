"""Simple in-memory memory structures for the first FUTURE-50 release."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MemoryRecord:
    key: str
    value: Any
    source: str = "local"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 1.0


class InMemoryMemory:
    """Thread-local, dependency-free memory implementation."""

    def __init__(self):
        self.records: dict[str, MemoryRecord] = {}

    def store(self, key: str, value: Any, source: str = "local", confidence: float = 1.0) -> MemoryRecord:
        record = MemoryRecord(key=key, value=value, source=source, timestamp=datetime.now(timezone.utc).isoformat(), confidence=confidence)
        self.records[key] = record
        return record

    def retrieve(self, key: str) -> MemoryRecord | None:
        return self.records.get(key)

    def list(self) -> list[MemoryRecord]:
        return list(self.records.values())
