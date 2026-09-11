"""Knowledge base stub for local semantic/keyword content retrieval."""

from dataclasses import dataclass


@dataclass
class KnowledgeRecord:
    topic: str
    body: str
    source: str = "local"


class KnowledgeBase:
    """Minimal knowledge base with searchable, extensible records."""

    def __init__(self):
        self.records: list[KnowledgeRecord] = []

    def add(self, topic: str, body: str, source: str = "local") -> KnowledgeRecord:
        record = KnowledgeRecord(topic=topic, body=body, source=source)
        self.records.append(record)
        return record

    def search(self, query: str) -> list[KnowledgeRecord]:
        query = query.lower()
        return [record for record in self.records if query in record.topic.lower() or query in record.body.lower()]
