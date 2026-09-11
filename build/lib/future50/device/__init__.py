"""Device provider and multi-device manager abstractions for FUTURE-50."""

from .providers import DeviceProvider, WindowsDeviceProvider, AndroidDeviceProvider, FutureDeviceProvider
from .manager import DeviceManager

__all__ = [
    "DeviceProvider",
    "WindowsDeviceProvider",
    "AndroidDeviceProvider",
    "FutureDeviceProvider",
    "DeviceManager",
]
