"""Plugin metadata and interface stubs for FUTURE-50 plugin system."""

from dataclasses import dataclass


@dataclass
class PluginMetadata:
    name: str
    version: str
    capabilities: list[str]
    permissions: list[str]


class Plugin:
    """Base plugin interface stub for optional capabilities."""

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata

    def describe(self) -> PluginMetadata:
        return self.metadata
