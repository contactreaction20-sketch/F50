"""Specialized local agent stubs for FUTURE-50.

This file exposes a replaceable agent registry for the requested
autonomous architecture without forcing a cloud dependency.
"""

from dataclasses import dataclass


@dataclass
class AgentProfile:
    name: str
    role: str
    capability: str
    local_only: bool = True


class AgentRegistry:
    """Registry for minimum required specialized agents."""

    def __init__(self):
        self.profiles = [
            AgentProfile("Orchestrator", "orchestrator", "goal planning"),
            AgentProfile("Planner", "planner", "task decomposition"),
            AgentProfile("Researcher", "researcher", "research retrieval"),
            AgentProfile("Coder", "coder", "coding"),
            AgentProfile("Debugger", "debugger", "bug isolation"),
            AgentProfile("Tester", "tester", "verification"),
            AgentProfile("Reviewer", "reviewer", "review"),
            AgentProfile("Security Analyst", "security", "trust"),
            AgentProfile("Data Analyst", "data", "analysis"),
            AgentProfile("Scientist", "scientist", "evidence"),
            AgentProfile("Writer", "writer", "generation"),
            AgentProfile("Designer", "designer", "design"),
            AgentProfile("Computer Operator", "computer_operator", "browser/filesystem"),
            AgentProfile("Knowledge Manager", "knowledge", "knowledge"),
            AgentProfile("Memory Manager", "memory", "memory"),
            AgentProfile("Optimizer", "optimizer", "performance"),
            AgentProfile("Learner", "learner", "learning"),
            AgentProfile("Self-Improvement Agent", "self_improvement", "evolution"),
        ]

    def list_profiles(self) -> list[AgentProfile]:
        return list(self.profiles)

    def get(self, name: str) -> AgentProfile | None:
        for profile in self.profiles:
            if profile.name.lower() == name.lower():
                return profile
        return None
