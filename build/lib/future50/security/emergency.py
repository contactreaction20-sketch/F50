"""Emergency-stop and privileged-action guard for FUTURE-50.

This provides a runtime-visible control object that can be toggled locally and
recorded in the audit stream. It is intentionally dependency-free and honest:
it represents a control surface and the system reports the stop state by
object property rather than by a fake command response.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EmergencyStopState(str, Enum):
    READY = "READY"
    STOPPED = "STOPPED"
    CANCELLED = "CANCELLED"


@dataclass
class EmergencyStopRecord:
    state: EmergencyStopState
    reason: str = "manual_requested"


class EmergencyStopManager:
    """Small, deterministic emergency-stop policy object."""

    def __init__(self):
        self.state = EmergencyStopState.READY
        self.reason = "none"

    def engage(self, reason: str = "manual_requested") -> EmergencyStopRecord:
        self.state = EmergencyStopState.STOPPED
        self.reason = reason
        return EmergencyStopRecord(state=self.state, reason=self.reason)

    def clear(self) -> EmergencyStopRecord:
        self.state = EmergencyStopState.READY
        self.reason = "none"
        return EmergencyStopRecord(state=self.state, reason=self.reason)

    def is_active(self) -> bool:
        return self.state != EmergencyStopState.READY
