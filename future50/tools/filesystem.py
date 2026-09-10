"""Filesystem tool interface stub for FUTURE-50 tool system.

The implementation intentionally remains dependency-free and local-only.
"""

from pathlib import Path


class FilesystemTool:
    """Minimal filesystem adapter with read/write/list operations."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)

    def read_text(self, relative_path: str) -> str:
        return (self.base_path / relative_path).read_text(encoding="utf-8")

    def write_text(self, relative_path: str, content: str) -> str:
        destination = self.base_path / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return str(destination)

    def list_dir(self, relative_path: str = ".") -> list[str]:
        return [item.name for item in (self.base_path / relative_path).iterdir()]
