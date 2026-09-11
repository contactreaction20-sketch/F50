"""CLI interface adapter for human-readable local interaction.

This repository intentionally remains web-free and laptop-local. The CLI adapter
can be used directly through the terminal without a browser or remote service.
"""

from ..core.chat import Future50Chat
from ..core.model_router import ModelRouter


class Future50CLI:
    """Simple command-line adapter that can be extended to a richer interface."""

    def __init__(self):
        self.chat = Future50Chat()
        self.router = ModelRouter()

    def run(self, task: str) -> str:
        model = self.router.route(task)
        response = self.chat.generate("user", task, model=model)
        return f"Routing task to {model.role.value} model: {response.text}"

    def interactive_loop(self, tagline: str = "FUTURE-50 local CLI") -> None:
        """Run a local command-line prompt loop without any web server dependency."""
        print(f"{tagline}. Type 'exit' or 'quit' to leave.")
        while True:
            try:
                task = input("future50> ")
            except EOFError:
                print("\nFUTURE-50 CLI session closed.")
                break

            if task.strip().lower() in {"exit", "quit", "bye"}:
                print("FUTURE-50 CLI session closed.")
                break

            if not task.strip():
                continue

            model = self.router.route(task)
            message = self.chat.generate("user", task, model=model)
            print(f"Route: {model.role.value}")
            print(message.text)
