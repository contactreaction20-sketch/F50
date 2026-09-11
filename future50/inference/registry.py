"""Model registry for FUTURE-50 local model providers.

This registry keeps the system model-agnostic while documenting the
available installed Ollama local models used by the current project.
"""

from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class ModelProfile:
    name: str
    family: str
    backend: str
    format: str = "gguf"
    quantization: str = "q4_K_M"
    parameters: str = "7B"
    context_length: int = 4096
    capabilities: tuple[str, ...] = ("chat",)
    ram_requirement: str = "4GB"
    vram_requirement: str = "0GB"
    status: str = "installed"
    active: bool = False


class ModelRegistry:
    """Static local registry for installed and selectable model profiles."""

    def __init__(self):
        self.profiles = [ModelProfile(
            name=os.getenv("F50_MODEL_NAME", "qwen2.5:7b-instruct-q4_K_M"),
            family="configured",
            backend="configured",
            format="API or GGUF",
            quantization="managed or q4_K_M",
            parameters="configured",
            context_length=8192,
            capabilities=("chat", "coding", "reasoning"),
            ram_requirement="0GB",
            vram_requirement="0GB",
            status="configured",
            active=True,
        )]

    def list_models(self) -> list[ModelProfile]:
        return list(self.profiles)

    def get_model(self, name: str) -> Optional[ModelProfile]:
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None

    def default_model(self) -> ModelProfile:
        return next((m for m in self.profiles if m.active), self.profiles[0])
