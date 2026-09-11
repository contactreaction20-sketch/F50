"""Local self-healing and recovery service for FUTURE-50.

This layer intentionally remains small and dependency-free: it records a
recovery attempt, tracks the action cause, and exposes a typed recovery
status without inventing unavailable hardware or cloud services.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryStatus(str, Enum):
    RETRYING = "retrying"
    RESTARTING = "restarting"
    REINITIALIZING = "reinitializing"
    FALLBACK = "fallback"
    FAILED = "failed"


@dataclass
class RecoveryAction:
    reason: str
    status: RecoveryStatus
    attempts: int
    message: str


class SelfHealingEngine:
    """A deterministic, local self-healing engine artifact."""

    def __init__(self):
        self.history: list[RecoveryAction] = []

    def recover(self, reason: str, retry_limit: int = 2) -> RecoveryAction:
        """Return a structured recovery record, never pretending a repair happened."""

        attempts = max(1, min(retry_limit, 3))
        status = RecoveryStatus.RETRYING
        if "provider unavailable" in reason.lower():
            status = RecoveryStatus.FAILED
            message = "Provider unavailable; local fallback or provider registry should be consulted."
        elif "tool" in reason.lower():
            status = RecoveryStatus.RESTARTING
            message = "Tool layer reported failure; minimum safe retry path initialized."
        else:
            message = "Recovery attempt recorded and bounded by the retry policy."

        action = RecoveryAction(reason=reason, status=status, attempts=attempts, message=message)
        self.history.append(action)
        return action
