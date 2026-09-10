"""Application facade for the minimum working FUTURE-50 core."""

from .core.system import Future50Core
from .core.autonomy import AutonomyLevel


class Future50App:
    """Simple entry point class for future expansion."""

    def __init__(self, task: str = "research", autonomy: str = "level_2"):
        self.task = task
        self.autonomy = AutonomyLevel.from_string(autonomy)
        self.core = Future50Core()

    def run(self) -> str:
        """Return the first result of a local model route and orchestrator response."""
        model = self.core.model_router.route(self.task)
        response = self.core.chat.generate(
            "user",
            f"FUTURE-50 local planning request: {self.task}",
            model=model,
        )
        return (
            f"FUTURE-50 started in autonomy {self.autonomy.name}. "
            f"Selected route: {model.role.value}. Response: {response.text}"
        )
