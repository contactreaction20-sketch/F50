"""Real local model provider adapters for FUTURE-50.

This keeps the architecture provider-agnostic while supporting a concrete,
installable local Ollama backend already present in the environment.
"""

from __future__ import annotations

import re
from typing import Optional, Any

try:
    import ollama
except Exception:  # pragma: no cover
    ollama = None


class ModelProvider:
    """Abstract local provider interface used by the app.

    Implementations expose a clean load/generate/chat interface that the rest
    of the project can call without coupling to a single model runtime.
    """

    def load(self) -> bool:
        raise NotImplementedError

    def generate(self, prompt: str, model: str = "qwen2.5:7b-instruct-q4_K_M") -> str:
        raise NotImplementedError

    def health_check(self) -> dict[str, Any]:
        raise NotImplementedError


class LocalOllamaProvider(ModelProvider):
    """Concrete local Ollama adapter.

    Uses the installed `ollama` Python client and a default model that is
    already present in the system registry.
    """

    def __init__(self, model: str = "qwen2.5:7b-instruct-q4_K_M"):
        self.model = model
        self.client = ollama.Client() if ollama is not None else None

    def load(self) -> bool:
        if self.client is None:
            return False
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def _same_language_instruction(self, prompt: str) -> str | None:
        """Return a clean system instruction that keeps the answer in the same language as the user."""
        if re.search(r'[\u0900-\u097F]', prompt):
            return "Respond in Hindi or Hinglish, matching the user’s language closely and avoiding random language switching."
        if re.search(r'[\u0600-\u06FF]', prompt):
            return "Respond in Urdu, matching the user’s language closely and avoiding random language switching."
        return "Respond in the same language as the user’s message; avoid cross-language drift."

    def generate(self, prompt: str, model: Optional[str] = None, system: Optional[str] = None) -> str:
        if self.client is None:
            return "Local model provider is unavailable: Ollama Python client is not installed."

        chosen = model or self.model
        try:
            payload = {
                "model": chosen,
                "prompt": prompt,
                "stream": False,
            }
            same_language = self._same_language_instruction(prompt)
            if system:
                payload["system"] = system
            elif same_language:
                payload["system"] = same_language

            response = self.client.generate(**payload)
            if hasattr(response, 'response'):
                return str(response.response).strip()
            if isinstance(response, dict):
                return str(response.get('response', 'No response generated.')).strip()
            return str(response).strip()
        except Exception as exc:
            return f"Local model inference failed: {exc}"

    def health_check(self) -> dict[str, Any]:
        try:
            if self.client is None:
                return {"status": "unavailable", "backend": "ollama", "reason": "ollama client missing"}
            self.client.list()
            return {"status": "healthy", "backend": "ollama", "model": self.model}
        except Exception as exc:
            return {"status": "unavailable", "backend": "ollama", "reason": str(exc)}


model_provider = LocalOllamaProvider()
