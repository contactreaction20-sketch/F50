"""Scheduler and persistable task state interface for future autonomous tasks."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TaskState(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Task:
    objective: str
    constraints: list[str] = field(default_factory=list)
    state: TaskState = TaskState.CREATED
    completed_steps: list[str] = field(default_factory=list)
    pending_steps: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    next_action: str = "research"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TaskScheduler:
    """Minimal task state and scheduling adapter."""

    def __init__(self):
        self.tasks: list[Task] = []
        self.emergency_stop = False

    def create_task(self, objective: str, constraints: list[str] | None = None) -> Task:
        task = Task(objective=objective, constraints=constraints or [], created_at=datetime.now(timezone.utc).isoformat())
        self.tasks.append(task)
        return task

    def list_tasks(self) -> list[Task]:
        return list(self.tasks)

    def trigger_emergency_stop(self) -> bool:
        self.emergency_stop = True
        return True
