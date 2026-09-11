"""Cognition interface stubs for planning and reasoning.

This module intentionally provides an extensible interface that can later be backed
by local reasoning models, planners, or symbolic architecture layers.
"""

from dataclasses import dataclass


@dataclass
class ReasoningResult:
    goal: str
    plan: list[str]
    confidence: float = 0.5


class ReasoningEngine:
    """Minimal planning adapter for the FUTURE-50 cognition layer."""

    def __init__(self):
        self.default_plan = ["observe", "understand", "plan", "act", "measure"]

    def plan(self, goal: str) -> ReasoningResult:
        return ReasoningResult(goal=goal, plan=self.default_plan)
