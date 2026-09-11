"""World model interface stubs for entities, events, relationships, and uncertainty.

This keeps future semantic graph structure isolated from the chat and model layers.
"""

from dataclasses import dataclass
from enum import Enum


class FactStatus(str, Enum):
    KNOWN = "known"
    INFERRED = "inferred"
    ASSUMED = "assumed"
    UNKNOWN = "unknown"
    CONTRADICTORY = "contradictory"


@dataclass
class WorldFact:
    subject: str
    predicate: str
    object_value: str
    status: FactStatus = FactStatus.KNOWN
    confidence: float = 1.0


class WorldModel:
    """A minimal world model graph container with status-aware facts."""

    def __init__(self):
        self.facts: list[WorldFact] = []

    def add_fact(self, subject: str, predicate: str, object_value: str, status: FactStatus = FactStatus.KNOWN, confidence: float = 1.0) -> WorldFact:
        fact = WorldFact(subject, predicate, object_value, status, confidence)
        self.facts.append(fact)
        return fact

    def list_facts(self) -> list[WorldFact]:
        return list(self.facts)
