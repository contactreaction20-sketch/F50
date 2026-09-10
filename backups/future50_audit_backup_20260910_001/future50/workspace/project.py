"""Workspace project metadata and project lifecycle adapters.

This keeps the user's project area locally inspectable and model-independent.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Project:
    name: str
    path: str
    description: str = "local project"
    created_files: list[str] = field(default_factory=list)


class ProjectWorkspace:
    """Minimal repository workspace abstraction."""

    def __init__(self, root: str = "."):
        self.root = Path(root)
        self.projects: dict[str, Project] = {}

    def create_project(self, name: str, description: str = "local project") -> Project:
        project = Project(name=name, path=str(self.root / name), description=description)
        self.projects[name] = project
        (self.root / name).mkdir(parents=True, exist_ok=True)
        return project

    def list_projects(self) -> list[Project]:
        return list(self.projects.values())
