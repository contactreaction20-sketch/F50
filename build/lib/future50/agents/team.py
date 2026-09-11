"""Adaptive multi-agent routing for the local web chat."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.model_router import LocalModel, ModelRole, ModelRouter


@dataclass(frozen=True)
class TeamPlan:
    lane: str
    lead: LocalModel
    specialists: tuple[str, ...]
    instruction: str


class MultiAgentTeam:
    """Select a focused expert lane without adding latency to simple prompts."""

    def __init__(self, router: ModelRouter | None = None):
        self.router = router or ModelRouter()

    def plan(self, task: str) -> TeamPlan:
        normalized = task.lower()
        if any(word in normalized for word in ("code", "python", "debug", "test", "bug", "function")):
            return TeamPlan(
                "coding",
                self._model(ModelRole.CODING),
                ("coder", "debugger", "tester"),
                "Act as a coding team: solve the task, check edge cases, and return executable, precise guidance.",
            )
        if any(word in normalized for word in ("research", "source", "compare", "evidence", "analyze")):
            return TeamPlan(
                "research",
                self._model(ModelRole.REASONING),
                ("researcher", "scientist", "reviewer"),
                "Act as a research team: separate facts from assumptions, reason carefully, and present a concise checked answer.",
            )
        if any(word in normalized for word in ("plan", "strategy", "architecture", "design")):
            return TeamPlan(
                "strategy",
                self._model(ModelRole.REASONING),
                ("planner", "designer", "reviewer"),
                "Act as a planning team: decompose the goal, choose practical steps, and review the plan for risks.",
            )
        return TeamPlan(
            "general",
            self._model(ModelRole.FAST),
            ("orchestrator", "writer"),
            "Act as a concise general assistant: understand the intent, answer directly, and verify the response before sending it.",
        )

    def _model(self, role: ModelRole) -> LocalModel:
        return next(model for model in self.router.models if model.role == role)

    def compose_system(self, plan: TeamPlan, language_instruction: str) -> str:
        specialists = ", ".join(plan.specialists)
        return (
            f"You are the lead of the FUTURE-50 {plan.lane} team. "
            f"Supporting specialists: {specialists}. {plan.instruction} "
            "Do not mention internal agents unless asked. Be useful and concise. "
            f"{language_instruction}"
        )
