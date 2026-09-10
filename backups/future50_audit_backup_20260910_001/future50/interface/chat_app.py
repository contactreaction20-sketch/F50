"""Local chat + coding app command manager.

This keeps the local software interface simple: chat request, command execution,
and coding task management all routed through one lightweight Python module.
"""

from ..coding.agent import CodingAgent
from ..coding.workspace import CodingWorkspaceManager
from ..tools.runner import LocalCommandRunner


class Future50ChatApp:
    """A local chat-and-coding manager for command-line interaction."""

    def __init__(self):
        self.coder = CodingAgent()
        self.workspace = CodingWorkspaceManager()
        self.runner = LocalCommandRunner(cwd=".")

    def handle(self, user_text: str) -> str:
        lower = user_text.lower()

        if "run" in lower or "test" in lower:
            if "run" in lower:
                result = self.runner.run("python -m pytest -q")
                return f"Command: {result.command}\nReturn code: {result.returncode}\n{result.stdout}"

        if "code" in lower or "python" in lower or "function" in lower or "debug" in lower:
            output = self.coder.handle(user_text)
            return f"Coding agent: {output}"

        return f"Chat reply: I received your local task: {user_text}"
