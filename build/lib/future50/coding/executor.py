"""Structured local code execution for FUTURE-50.

Provides a deterministic Python execution adapter that reports the structured
result of a snippet or a file and remains dependency-free for the laptop UI.
"""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
import sys
from pathlib import Path


@dataclass
class CodeExecutionResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    duration_ms: int = 0


class LocalCodeExecutionEngine:
    """Execute a Python snippet locally and capture a structured result."""

    def __init__(self, cwd: str = "."):
        self.cwd = Path(cwd)

    def run_python_snippet(self, snippet: str) -> CodeExecutionResult:
        """Execute a Python snippet and return cleanly typed output."""

        file_path = self.cwd / "future50_tmp_exec.py"
        file_path.write_text(snippet, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, str(file_path)],
                cwd=str(self.cwd),
                shell=False,
                text=True,
                capture_output=True,
                timeout=10,
            )
            return CodeExecutionResult(
                command=f"{sys.executable} {file_path}",
                returncode=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_ms=0,
            )
        except subprocess.TimeoutExpired as exc:
            return CodeExecutionResult(
                command=f"{sys.executable} {file_path}",
                returncode=-1,
                stdout=exc.stdout or "",
                stderr=f"timeout: {exc.stderr or ''}",
                duration_ms=0,
            )
        finally:
            if file_path.exists():
                file_path.unlink(missing_ok=True)
