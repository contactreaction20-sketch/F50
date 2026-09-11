"""A minimal dependency-free local RAG implementation for FUTURE-50.

This keeps the architecture provider-agnostic while providing an implementable
retrieval layer that works in a pure-Python local workspace without external
vector stores or cloud credentials.

The extension here introduces an online research fallback that can draft a
research pass from a web search endpoint or a generic URL fetch when the task
is outside the document corpus and local knowledge store.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable
import urllib.parse
import urllib.request


@dataclass
class LocalRAGResult:
    """A retrieved chunk result packed with enough metadata for a local answer.

    The runtime answer path can use the text and source fields directly for
    context injection into the local provider prompt or for GUI/source trace.
    """

    text: str
    source: str
    score: float


class LocalKnowledgeRAG:
    """Local-first knowledge retrieval implemented as a tiny chunk store.

    The implementation intentionally stays dependency-free and deterministic:
    documents are ingested from files or strings, split into simple chunks, and
    scored with a token-overlap heuristic that can run fully on the laptop.

    New behavior: if the local corpus fails to answer a task, the object can
    attempt an online search fetch and turn the top snippet into a research result.
    """

    def __init__(self):
        self.documents: list[LocalRAGResult] = []

    def ingest_text(self, text: str, source: str = "local") -> list[LocalRAGResult]:
        """Ingest a string and return the list of stored chunks.

        Chunks are created by splitting on sentence boundaries and trimming
        whitespace. The empty string is ignored.
        """

        chunks = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", text.strip()) if chunk.strip()]
        added: list[LocalRAGResult] = []
        for chunk in chunks:
            self.documents.append(LocalRAGResult(text=chunk, source=source, score=1.0))
            added.append(self.documents[-1])
        return added

    def ingest_path(self, path: str | Path) -> list[LocalRAGResult]:
        """Ingest a text file from disk."""

        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"RAG input file not found: {file_path}")
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return self.ingest_text(text, source=str(file_path))

    def search(self, query: str, top_k: int = 3) -> list[LocalRAGResult]:
        """Return the most relevant chunk results by token overlap score.

        A simple and deterministic ranking algorithm is used so the runtime is
        testable without a vector database. The result is sorted descending by
        overlap count and normalized relevance.
        """

        query_tokens = self._tokens(query)
        if not query_tokens:
            return []

        scored: list[LocalRAGResult] = []
        for doc in self.documents:
            doc_tokens = self._tokens(doc.text)
            overlap = len(set(query_tokens) & set(doc_tokens))
            if overlap == 0:
                continue
            total = max(1, len(set(query_tokens)))
            score = (overlap / total) + min(0.3, len(doc.text.split()) / 1000)
            scored.append(LocalRAGResult(text=doc.text, source=doc.source, score=score))

        scored.sort(key=lambda result: result.score, reverse=True)
        return scored[:top_k]

    def research_online(self, query: str, top_k: int = 1) -> list[LocalRAGResult]:
        """Optional online research fallback for unknown tasks.

        The method does a deterministic HTTP GET against a public search query
        endpoint when network access is available and converts the page snippet
        or the search page response into a LocalRAGResult document record. If the
        network fetch fails, this method quietly downgrades to an empty result set.
        """
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode("utf-8", errors="ignore")
        except Exception:
            return []

        snippets = []
        for match in re.findall(r'(?i)(?:result__a|<a[^>]+href=["\'][^"\']+["\'][^>]*>)([^<]+)</a>|(?:<span[^>]+class=["\']snippet["\'][^>]*>)([^<]+)</span>', html):
            text = " ".join(part for part in match if part).strip()
            if text:
                snippets.append(text)

        if not snippets:
            snippets = [f"Online research fallback: {query} -> plan, fetch, inspect, execute locally."]

        results = []
        for idx, text in enumerate(snippets[:top_k], start=1):
            score = 1.0 / idx
            results.append(LocalRAGResult(text=f"{text}", source="online_search", score=score))
        return results

    def execute_unknown_task(self, query: str) -> list[LocalRAGResult]:
        """Return online research evidence for an unknown task, then let the planner run from that evidence."""
        local_hits = self.search(query, top_k=3)
        if local_hits:
            return local_hits
        return self.research_online(query, top_k=3)

    @staticmethod
    def _tokens(text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Z0-9_-]+", text.lower())
        return {token for token in tokens if len(token) >= 2}
