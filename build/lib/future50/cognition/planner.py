"""Minimal planning engine and goal decomposition stubs.

These interfaces keep planning inside the cognition layer and decouple
it from the chat and model transport layers.
"""

from dataclasses import dataclass


@dataclass
class GoalNode:
    mission: str
    objective: str
    project: str
    task: str
    subtask: str
    action: str


class PlanningEngine:
    """Simple hierarchical task decomposition adapter."""

    def __init__(self):
        self.last_goal: GoalNode | None = None

    def decompose(self, mission: str, objective: str, project: str = "local") -> GoalNode:
        node = GoalNode(
            mission=mission,
            objective=objective,
            project=project,
            task=objective,
            subtask="create initial executable step",
            action="observe",
        )
        self.last_goal = node
        return node
