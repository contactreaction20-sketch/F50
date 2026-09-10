"""Model routing primitives for a local-first AI operating system."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..inference.providers import model_provider


class ModelRole(str, Enum):
    FAST = "fast"
    CODING = "coding"
    REASONING = "reasoning"
    VISION = "vision"
    SMALL = "small"
    GENERAL = "general"


@dataclass
class LocalModel:
    """Minimal local model abstraction."""

    name: str
    role: ModelRole
    context_window: int = 4096
    provider: str = "local"

    def infer(self, prompt: str) -> str:
        clean_prompt = prompt.strip()
        if not clean_prompt:
            return f"FUTURE-50 {self.role.value.upper()} route is ready."

        # Provider-only inference path. No old route phrase is allowed to
        # masquerade as a real model response.
        system_instruction = model_provider._same_language_instruction(clean_prompt)
        try:
            reply = model_provider.generate(
                clean_prompt,
                model="qwen2.5:7b-instruct-q4_K_M",
                system=system_instruction,
            )
        except TypeError:
            reply = model_provider.generate(clean_prompt, model="qwen2.5:7b-instruct-q4_K_M")

        if reply.startswith("Local model inference failed:") or "Local model provider is unavailable" in reply:
            return reply
        if "provider unavailable" in reply.lower():
            return reply
        return reply


class ModelRouter:
    """Selects a model based on task hints and hardware-aware metadata."""

    def __init__(self, models: list[LocalModel] | None = None):
        self.models = models or [
            LocalModel("qwen2.5:7b-instruct-q4_K_M", ModelRole.FAST),
            LocalModel("qwen2.5-coder:7b", ModelRole.CODING),
            LocalModel("llama3:latest", ModelRole.REASONING),
            LocalModel("dolphin-llama3:latest", ModelRole.VISION),
            LocalModel("orca-mini:latest", ModelRole.SMALL),
        ]

    def route(self, task: str, complexity: str = "simple") -> LocalModel:
        normalized = task.lower()
        if any(word in normalized for word in ["code", "python", "debug", "test", "bug"]):
            return next(m for m in self.models if m.role == ModelRole.CODING)
        if any(word in normalized for word in ["plan", "reason", "strategy"]):
            return next(m for m in self.models if m.role == ModelRole.REASONING)
        if any(word in normalized for word in ["vision", "image", "screen"]):
            return next(m for m in self.models if m.role == ModelRole.VISION)
        if complexity == "simple" or task.strip() == "":
            return next(m for m in self.models if m.role == ModelRole.FAST)
        return next(m for m in self.models if m.role == ModelRole.GENERAL)
