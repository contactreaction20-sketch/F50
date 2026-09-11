"""Real local model provider adapters for FUTURE-50.

This keeps the architecture provider-agnostic while supporting a concrete,
installable local Ollama backend already present in the environment.
"""

from __future__ import annotations

import re
import json
import os
from urllib import request as http_request
from urllib.error import HTTPError, URLError
from typing import Optional, Any

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
    """OpenAI-compatible NVIDIA provider kept under the legacy class name."""

    def __init__(self, model: str = "nvidia/nemotron-3-super-120b-a12b"):
        self.model = model
        self.remote_url = os.getenv("F50_MODEL_API_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
        self.remote_key = os.getenv("F50_MODEL_API_KEY", "")
        self.remote_model = os.getenv("F50_MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b")

    def load(self) -> bool:
        return bool(self.remote_key)

    def _same_language_instruction(self, prompt: str) -> str | None:
        """Return a clean system instruction that keeps the answer in the same language as the user."""
        if re.search(r'[\u0900-\u097F]', prompt):
            return "Respond in Hindi or Hinglish, matching the user’s language closely and avoiding random language switching."
        if re.search(r'[\u0600-\u06FF]', prompt):
            return "Respond in Urdu, matching the user’s language closely and avoiding random language switching."
        return "Respond in the same language as the user’s message; avoid cross-language drift."

    def generate(self, prompt: str, model: Optional[str] = None, system: Optional[str] = None) -> str:
        return self._remote_generate(prompt, model=model, system=system)

    def _remote_generate(self, prompt: str, model: Optional[str], system: Optional[str]) -> str:
        if not self.remote_key:
            return "Remote model provider is unavailable: F50_MODEL_API_KEY is not configured."
        payload = {
            "model": self.remote_model,
            "messages": [
                {"role": "system", "content": system or self._same_language_instruction(prompt)},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.25,
            "max_tokens": 1024,
        }
        body = json.dumps(payload).encode("utf-8")
        http_request_obj = http_request.Request(
            f"{self.remote_url}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.remote_key}"},
            method="POST",
        )
        try:
            with http_request.urlopen(http_request_obj, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
            return str(data["choices"][0]["message"]["content"]).strip()
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
            return f"Remote model inference failed: {exc}"

    def stream_generate(self, prompt: str, model: Optional[str] = None, system: Optional[str] = None):
        """Yield NVIDIA model tokens as soon as the online provider produces them."""
        yield from self._remote_stream_generate(prompt, model=model, system=system)

    def _remote_stream_generate(self, prompt: str, model: Optional[str], system: Optional[str]):
        if not self.remote_key:
            yield "Remote model provider is unavailable: F50_MODEL_API_KEY is not configured."
            return
        payload = {
            "model": self.remote_model,
            "messages": [
                {"role": "system", "content": system or self._same_language_instruction(prompt)},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.25,
            "max_tokens": 1024,
            "stream": True,
        }
        http_request_obj = http_request.Request(
            f"{self.remote_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.remote_key}"},
            method="POST",
        )
        try:
            with http_request.urlopen(http_request_obj, timeout=45) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        return
                    event = json.loads(data)
                    delta = event.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        yield str(delta)
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
            yield f"Remote model inference failed: {exc}"

    def health_check(self) -> dict[str, Any]:
        try:
            if not self.remote_key:
                return {"status": "unavailable", "backend": "nvidia", "reason": "API key missing"}
            return {"status": "configured", "backend": "nvidia", "model": self.remote_model}
        except Exception as exc:
            return {"status": "unavailable", "backend": "nvidia", "reason": str(exc)}


model_provider = LocalOllamaProvider()
