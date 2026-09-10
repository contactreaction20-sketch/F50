"""Monitoring and observability interface stubs for health, logs, and telemetry."""

from dataclasses import dataclass


@dataclass
class HealthSnapshot:
    cpu: float = 0.0
    ram: float = 0.0
    disk: float = 0.0
    status: str = "nominal"


class MonitoringService:
    """Local telemetry service for health and resource observation."""

    def __init__(self):
        self.snapshots: list[HealthSnapshot] = []

    def sample(self, cpu: float = 0.0, ram: float = 0.0, disk: float = 0.0) -> HealthSnapshot:
        snapshot = HealthSnapshot(cpu=cpu, ram=ram, disk=disk)
        self.snapshots.append(snapshot)
        return snapshot
