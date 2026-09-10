"""A minimal orchestrator agent for the FUTURE-50 system."""

from dataclasses import dataclass


@dataclass
class AgentPlan:
    objective: str
    required_capabilities: list[str]
    model_role: str
    notes: str


class OrchestratorAgent:
    """Chooses a model role and capability list from a user task."""

    def __init__(self, core):
        self.core = core

    def plan(self, task: str) -> AgentPlan:
        task_lower = task.lower()
        capabilities = ["local_model", "memory"]
        if any(word in task_lower for word in ["code", "debug", "test"]):
            model_role = "coding"
            capabilities.append("coding")
        elif any(word in task_lower for word in ["reason", "plan", "research"]):
            model_role = "reasoning"
            capabilities.append("knowledge")
        else:
            model_role = "fast"
        return AgentPlan(
            objective=task,
            required_capabilities=capabilities,
            model_role=model_role,
            notes="Plan created by local orchestrator stub.",
        )
