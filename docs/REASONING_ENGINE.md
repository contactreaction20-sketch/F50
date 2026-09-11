# Reasoning Engine

Current connected reasoning is adaptive lane selection in `future50/agents/team.py` plus intent detection in `ContextManager`.

- General questions use the fast lane.
- Coding/debug tasks use coding, debugger, and tester specialist guidance.
- Research tasks use research, scientist, and reviewer guidance.
- Planning tasks use planner, designer, and reviewer guidance.

The existing `ReasoningEngine` and `PlanningEngine` remain reusable low-level adapters. Hidden chain-of-thought is not exposed. Multi-step tool reasoning is still partial until the task service invokes the existing runtime action loop.
