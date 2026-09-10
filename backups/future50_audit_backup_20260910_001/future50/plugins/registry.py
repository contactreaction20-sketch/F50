"""Plugin registry for loading local and optional plugins.

This is a clean interface stub that can later support dependency metadata,
permission checks, and optional adapter registration.
"""

from dataclasses import dataclass


@dataclass
class PluginRegistration:
    name: str
    version: str
    capabilities: list[str]


class PluginRegistry:
    """Simple registry for local plugin registration."""

    def __init__(self):
        self.plugins: list[PluginRegistration] = []

    def register(self, name: str, version: str = "0.1.0", capabilities: list[str] | None = None) -> PluginRegistration:
        plugin = PluginRegistration(name=name, version=version, capabilities=capabilities or [])
        self.plugins.append(plugin)
        return plugin

    def list_plugins(self) -> list[PluginRegistration]:
        return list(self.plugins)
