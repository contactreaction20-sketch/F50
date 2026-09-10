"""System aggregator for the FUTURE-50 minimum core."""

from ..agents.orchestrator import OrchestratorAgent
from ..core.chat import Future50Chat
from ..core.model_router import ModelRouter
from ..core.permissions import PermissionManager
from ..memory.memory import InMemoryMemory
from ..knowledge.knowledge import KnowledgeBase


class Future50Core:
    """Initial system core assembling the key minimal subsystems."""

    def __init__(self):
        self.chat = Future50Chat()
        self.model_router = ModelRouter()
        self.permission_manager = PermissionManager()
        self.memory = InMemoryMemory()
        self.knowledge = KnowledgeBase()
        self.orchestrator = OrchestratorAgent(self)

    def route(self, task: str) -> str:
        """Convenience method for selecting a route and returning role metadata."""
        model = self.model_router.route(task)
        return model.role.value
