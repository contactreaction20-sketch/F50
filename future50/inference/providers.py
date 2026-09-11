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
        self.remote_url = os.getenv("F50_MODEL_API_URL", "").rstrip("/")
        self.remote_key = os.getenv("F50_MODEL_API_KEY", "")
        self.remote_model = os.getenv("F50_MODEL_NAME", model)

    def load(self) -> bool:
        if self.remote_url:
            return bool(self.remote_key)
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
        if self.remote_url:
            return self._remote_generate(prompt, model=model, system=system)
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
            "max_tokens": 512,
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
        """Yield local model tokens as soon as Ollama produces them."""
        if self.remote_url:
            yield from self._remote_stream_generate(prompt, model=model, system=system)
            return
        if self.client is None:
            yield "Local model provider is unavailable: Ollama Python client is not installed."
            return

        chosen = model or self.model
        try:
            payload = {
                "model": chosen,
                "prompt": prompt,
                "stream": True,
                "keep_alive": "10m",
                "options": {"temperature": 0.25, "num_predict": 256},
            }
            same_language = self._same_language_instruction(prompt)
            if system or same_language:
                payload["system"] = system or same_language
            for chunk in self.client.generate(**payload):
                if hasattr(chunk, "response"):
                    token = chunk.response
                elif isinstance(chunk, dict):
                    token = chunk.get("response", "")
                else:
                    token = str(chunk)
                if token:
                    yield str(token)
        except Exception as exc:
            yield f"Local model inference failed: {exc}"

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
            "max_tokens": 512,
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
            if self.remote_url:
                if not self.remote_key:
                    return {"status": "unavailable", "backend": "remote", "reason": "API key missing"}
                return {"status": "configured", "backend": "remote", "model": self.remote_model}
            if self.client is None:
                return {"status": "unavailable", "backend": "ollama", "reason": "ollama client missing"}
            self.client.list()
            return {"status": "healthy", "backend": "ollama", "model": self.model}
        except Exception as exc:
            return {"status": "unavailable", "backend": "ollama", "reason": str(exc)}


model_provider = LocalOllamaProvider()
