"""Local inference adapters and provider plumbing for FUTURE-50.

This package centralizes the real local model provider interface used by
Future50Chat and the LocalModel abstraction.
"""

from .providers import ModelProvider, LocalOllamaProvider, model_provider
from .registry import ModelRegistry, ModelProfile
from .manager import LocalModelManager

__all__ = [
    "ModelProvider",
    "LocalOllamaProvider",
    "model_provider",
    "ModelRegistry",
    "ModelProfile",
    "LocalModelManager",
]
