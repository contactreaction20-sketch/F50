"""Multi-device registry and capability discovery manager for FUTURE-50."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceRecord:
    name: str
    platform: str
    capabilities: list[str]
    connected: bool = False
    authorized: bool = False
    status: str = "not_ready"


class DeviceManager:
    """A small provider-based multi-device registry.

    The main goal is to keep the device-aware architecture explicit and
    provider-first, avoiding hard-coded assumptions that every platform is
    reachable from the same laptop environment.
    """

    def __init__(self):
        self.devices: list[DeviceRecord] = []

    def register(self, provider: Any) -> DeviceRecord:
        info = provider.discover()
        record = DeviceRecord(
            name=provider.__class__.__name__,
            platform=info.get("platform", provider.platform),
            capabilities=list(info.get("capabilities", [])),
            connected=bool(info.get("connected", False)),
            authorized=info.get("authorization") == "FULL_LOCAL_CONTROL" or info.get("authorization") is None,
            status=info.get("status", "not_ready"),
        )
        self.devices.append(record)
        return record

    def list_devices(self) -> list[DeviceRecord]:
        return list(self.devices)
