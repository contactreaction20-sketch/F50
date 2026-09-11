"""Local storage interface for a memory/knowledge-first architecture.

This is intentionally dependency-free and serves as a local DB adapter stub.
"""

from dataclasses import dataclass


@dataclass
class LocalRow:
    collection: str
    key: str
    value: str


class LocalDatabase:
    """Minimal key-value style database adapter."""

    def __init__(self):
        self.rows: list[LocalRow] = []

    def put(self, collection: str, key: str, value: str) -> LocalRow:
        row = LocalRow(collection, key, value)
        self.rows.append(row)
        return row

    def get(self, collection: str, key: str) -> LocalRow | None:
        for row in self.rows:
            if row.collection == collection and row.key == key:
                return row
        return None
