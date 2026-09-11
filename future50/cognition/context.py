"""Structured context, intent, and durable conversation memory for FUTURE-50."""

from __future__ import annotations

import json
import re
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ContextTurn:
    role: str
    text: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    topic: str = ""
    importance: float = 0.5
    source: str = "conversation"


@dataclass
class ContextSnapshot:
    session_id: str
    current_message: str
    intent: tuple[str, ...]
    references: dict[str, str]
    recent_turns: list[ContextTurn]
    relevant_turns: list[ContextTurn]
    unresolved: list[str]
    confidence: float

    def prompt(self) -> str:
        sections = []
        if self.relevant_turns:
            transcript = "\n".join(f"{turn.role.upper()}: {turn.text}" for turn in self.relevant_turns)
            sections.append(f"RELEVANT CONVERSATION:\n{transcript}")
        if self.references:
            sections.append("RESOLVED REFERENCES:\n" + "\n".join(f"{key}: {value}" for key, value in self.references.items()))
        if self.unresolved:
            sections.append("UNCERTAIN REFERENCES: " + ", ".join(self.unresolved))
        sections.append(f"CURRENT USER MESSAGE: {self.current_message}")
        return "\n\n".join(sections)


class ContextManager:
    """Selects useful context instead of blindly concatenating a transcript."""

    REFERENCE_WORDS = {"this", "that", "it", "same", "previous", "earlier", "continue", "again"}
    INTENT_RULES = {
        "CODE": ("code", "python", "function", "class", "implement"),
        "DEBUG": ("debug", "bug", "error", "fix", "failing"),
        "RESEARCH": ("research", "source", "evidence", "compare", "analyze"),
        "PLANNING": ("plan", "strategy", "roadmap", "steps", "architecture"),
        "TASK": ("task", "todo", "continue", "finish", "build"),
        "MEMORY_QUERY": ("remember", "forgot", "what did we", "do you know"),
        "QUESTION": ("what", "why", "how", "when", "where", "who", "?"),
    }

    def __init__(self, root: str | Path = "memory", max_turns: int = 40):
        self.root = Path(root)
        self.path = self.root / "cognitive_sessions.json"
        self.legacy_path = self.root / "future50_sessions.json"
        self.max_turns = max_turns
        self.sessions: dict[str, list[ContextTurn]] = {}
        self.lock = threading.RLock()
        self.load()

    def load(self) -> None:
        try:
            source = self.path if self.path.exists() else self.legacy_path
            raw = json.loads(source.read_text(encoding="utf-8"))
            raw = {
                session: [
                    turn if "timestamp" in turn else {
                        "role": turn.get("role", "assistant"),
                        "text": turn.get("text", ""),
                    }
                    for turn in turns
                ]
                for session, turns in raw.items()
            }
            self.sessions = {session: [ContextTurn(**turn) for turn in turns] for session, turns in raw.items()}
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
            self.sessions = {}

    def save(self) -> None:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            payload = {session: [asdict(turn) for turn in turns] for session, turns in self.sessions.items()}
            temporary.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            temporary.replace(self.path)
        except OSError:
            pass

    def remember(self, session_id: str, role: str, text: str, importance: float = 0.5, topic: str = "") -> ContextTurn:
        turn = ContextTurn(role=role, text=text.strip(), importance=max(0.0, min(1.0, importance)), topic=topic or self.topic(text))
        with self.lock:
            turns = self.sessions.setdefault(session_id, [])
            turns.append(turn)
            self.sessions[session_id] = turns[-self.max_turns:]
            self.save()
        return turn

    def remember_many(self, session_id: str, entries: list[tuple[str, str, float]]) -> list[ContextTurn]:
        """Append several turns with one persistence write."""
        with self.lock:
            turns = self.sessions.setdefault(session_id, [])
            added = [
                ContextTurn(
                    role=role,
                    text=text.strip(),
                    importance=max(0.0, min(1.0, importance)),
                    topic=self.topic(text),
                )
                for role, text, importance in entries
            ]
            turns.extend(added)
            self.sessions[session_id] = turns[-self.max_turns:]
            self.save()
            return added

    def snapshot(self, session_id: str, message: str) -> ContextSnapshot:
        with self.lock:
            turns = list(self.sessions.get(session_id, []))
        intent = self.detect_intent(message)
        references, unresolved = self.resolve_references(message, turns)
        query_tokens = self.tokens(message) | self.tokens(" ".join(references.values()))
        scored = []
        for index, turn in enumerate(turns):
            overlap = len(query_tokens & self.tokens(turn.text))
            recency = (index + 1) / max(1, len(turns))
            score = overlap * 2 + turn.importance + recency * 0.4
            if turn.topic and turn.topic in message.lower():
                score += 1.0
            scored.append((score, turn))
        relevant = [turn for _, turn in sorted(scored, key=lambda item: item[0], reverse=True)[:12]]
        recent = turns[-8:]
        confidence = 0.95 if not unresolved else max(0.35, 0.85 - len(unresolved) * 0.15)
        return ContextSnapshot(session_id, message, intent, references, recent, relevant, unresolved, confidence)

    def detect_intent(self, message: str) -> tuple[str, ...]:
        normalized = message.lower()
        matches = [intent for intent, words in self.INTENT_RULES.items() if any(word in normalized for word in words)]
        return tuple(matches or ["CONVERSATION"])

    def resolve_references(self, message: str, turns: list[ContextTurn]) -> tuple[dict[str, str], list[str]]:
        normalized = message.lower()
        references: dict[str, str] = {}
        unresolved: list[str] = []
        if not turns:
            return references, [word for word in self.REFERENCE_WORDS if word in normalized and word in {"this", "that", "it", "continue"}]
        latest_user = next((turn.text for turn in reversed(turns) if turn.role == "user"), "")
        latest_topic = next((turn.topic for turn in reversed(turns) if turn.topic), "")
        if any(word in normalized for word in ("this", "it", "that", "same")):
            if latest_user:
                references["current_subject"] = latest_user
            else:
                unresolved.append("current_subject")
        if any(word in normalized for word in ("previous", "earlier")):
            previous = [turn.text for turn in turns if turn.role == "user"]
            if len(previous) >= 2:
                references["previous_subject"] = previous[-2]
            else:
                unresolved.append("previous_subject")
        if "continue" in normalized:
            references["active_task"] = latest_user or latest_topic
        return references, unresolved

    def topic(self, text: str) -> str:
        words = [word for word in self.tokens(text) if word not in {"this", "that", "what", "please", "the", "and"}]
        return " ".join(words[:4])

    @staticmethod
    def tokens(text: str) -> set[str]:
        return set(re.findall(r"[\w-]{2,}", text.lower()))
