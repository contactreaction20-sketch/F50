"""Unified local tool registry for FUTURE-50.

This registry keeps tool metadata, permission class, timeout, availability,
execution handler, and audit metadata in a single typed interface. It does
not invent a provider or hidden command execution path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from future50.core.permissions import PermissionLevel, PermissionManager


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, str]
    output_schema: dict[str, str]
    version: str = "1.0"
    permission_level: PermissionLevel = PermissionLevel.READ
    risk_level: str = "LOW_RISK"
    timeout: int = 5
    availability: str = "AVAILABLE"
    execution_handler: Callable[[dict[str, Any]], Any] | None = None
    audit_metadata: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """Minimal dependency-free dynamic registry of local tools."""

    def __init__(self):
        self.tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> ToolSpec:
        self.tools[tool.name] = tool
        return tool

    def execute(self, name: str, args: dict[str, Any], manager: PermissionManager | None = None, permission: PermissionLevel = PermissionLevel.READ) -> Any:
        spec = self.tools.get(name)
        if spec is None:
            raise KeyError(f"Tool not found: {name}")
        if spec.execution_handler is None:
            raise RuntimeError(f"No execution handler registered for {name}")
        return spec.execution_handler(args)

    def list_tools(self) -> list[ToolSpec]:
        return list(self.tools.values())
