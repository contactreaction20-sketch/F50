"""Local command runner adapter for FUTURE-50.

This is intentionally dependency-free and suitable for a laptop-local coding/test loop.
It runs shell commands safely in the current workspace and captures text output.
"""

import subprocess
from dataclasses import dataclass


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


class LocalCommandRunner:
    """Execute local shell commands and return structured capture output."""

    def __init__(self, cwd: str = "."):
        self.cwd = cwd

    def run(self, command: str) -> CommandResult:
        proc = subprocess.run(
            command,
            cwd=self.cwd,
            shell=True,
            text=True,
            capture_output=True,
        )
        return CommandResult(
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
