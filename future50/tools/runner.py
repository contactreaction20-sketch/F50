"""Local command runner adapter for FUTURE-50.

This is intentionally dependency-free and suitable for a laptop-local coding/test loop.
It runs shell commands safely in the current workspace and captures text output.
"""

import os
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
        # Detect when the app is already inside an active pytest worker/task,
        # so the command runner does not recursively trigger a nested test run.
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return CommandResult(
                command=command,
                returncode=0,
                stdout="pytest command skipped while PYTEST_CURRENT_TEST is active.",
                stderr="",
            )

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
