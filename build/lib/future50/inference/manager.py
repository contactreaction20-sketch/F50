"""Model manager for FUTURE-50 local inference.

Keeps the provider abstraction clean and exposes the basic model
operations the repository already expects in the prompt.
"""

from __future__ import annotations

from typing import Any

from .providers import LocalOllamaProvider, model_provider
from .registry import ModelRegistry


class LocalModelManager:
    """Small operational wrapper around the registry and provider."""

    def __init__(self, provider: LocalOllamaProvider | None = None):
        self.registry = ModelRegistry()
        self.provider = provider or model_provider

    def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "name": profile.name,
                "family": profile.family,
                "backend": profile.backend,
                "format": profile.format,
                "quantization": profile.quantization,
                "parameters": profile.parameters,
                "context_length": profile.context_length,
                "capabilities": list(profile.capabilities),
                "status": profile.status,
                "active": profile.active,
            }
            for profile in self.registry.list_models()
        ]

    def health(self) -> dict[str, Any]:
        return self.provider.health_check()

    def generate(self, prompt: str, model: str | None = None) -> str:
        return self.provider.generate(prompt, model=model)

    def test_model(self, model: str | None = None) -> bool:
        health = self.provider.health_check()
        if health.get("status") != "healthy":
            return False
        response = self.provider.generate("hello", model=model or self.provider.model)
        return bool(response and "Local model" not in response)
