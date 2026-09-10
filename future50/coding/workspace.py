"""Local workspace coding manager for the FUTURE-50 coding layer.

This adapter keeps a project workspace list and a minimal coding task manager.
"""

from dataclasses import dataclass


@dataclass
class CodeTask:
    name: str
    objective: str
    status: str = "planned"


class CodingWorkspaceManager:
    """Simple local coding manager for files, tasks, and code generation stubs."""

    def __init__(self):
        self.tasks: list[CodeTask] = []
        self.files: list[str] = []

    def add_task(self, name: str, objective: str) -> CodeTask:
        task = CodeTask(name=name, objective=objective)
        self.tasks.append(task)
        return task

    def add_file(self, name: str) -> str:
        self.files.append(name)
        return name

    def list_tasks(self) -> list[CodeTask]:
        return list(self.tasks)
