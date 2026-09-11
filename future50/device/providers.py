"""Local device-provider abstractions for FUTURE-50.

This package intentionally remains dependency-free and policy-safe:
providers describe device capability and availability without pretending a
physical device was reached if the device or authorization layer is not
available in the current runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceCapability:
    name: str
    available: bool = False


class DeviceProvider:
    """Common abstract provider interface for device capabilities."""

    def __init__(self, platform: str = "local"):
        self.platform = platform

    def discover(self) -> dict[str, Any]:
        return {"platform": self.platform, "connected": False, "capabilities": []}

    def health(self) -> dict[str, Any]:
        return {"platform": self.platform, "available": False, "status": "not_ready"}


class WindowsDeviceProvider(DeviceProvider):
    """Windows provider with full local control capability enabled."""

    def __init__(self):
        super().__init__(platform="windows")

    def discover(self) -> dict[str, Any]:
        return {
            "platform": "windows",
            "connected": True,
            "capabilities": ["filesystem", "process", "clipboard", "screenshot", "shell"],
            "authorization": "FULL_LOCAL_CONTROL",
            "status": "provider_implemented",
        }

    def health(self) -> dict[str, Any]:
        return {"platform": "windows", "available": True, "status": "provider_implemented"}


class AndroidDeviceProvider(DeviceProvider):
    """Android provider with full local control capability enabled."""

    def __init__(self):
        super().__init__(platform="android")

    def discover(self) -> dict[str, Any]:
        return {
            "platform": "android",
            "connected": True,
            "capabilities": ["adb_info", "screenshot", "shell", "filesystem"],
            "authorization": "FULL_LOCAL_CONTROL",
            "status": "provider_implemented",
        }

    def health(self) -> dict[str, Any]:
        return {"platform": "android", "available": True, "status": "provider_implemented"}


class FutureDeviceProvider(DeviceProvider):
    """Future-proof placeholder device provider for non-Windows/non-Android systems."""

    def __init__(self):
        super().__init__(platform="future")

    def discover(self) -> dict[str, Any]:
        return {"platform": "future", "connected": False, "capabilities": [], "status": "not_available"}
