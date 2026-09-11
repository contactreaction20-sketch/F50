from future50.agents.team import MultiAgentTeam
from future50.cognition.context import ContextManager
from future50.research.local_rag import LocalKnowledgeRAG
from future50.web.server import ChatWebHandler


def test_context_memory_survives_reload_and_retrieves_original_fact(tmp_path):
    first = ContextManager(root=tmp_path)
    first.remember("session", "user", "The active project is Aurora", importance=1.0)
    first.remember("session", "assistant", "Aurora is pending verification")

    second = ContextManager(root=tmp_path)
    snapshot = second.snapshot("session", "What is the active project?")

    assert any("Aurora" in turn.text for turn in snapshot.relevant_turns)
    assert snapshot.confidence > 0.5


def test_context_handles_long_conversation_and_follow_up_reference(tmp_path):
    manager = ContextManager(root=tmp_path, max_turns=50)
    for index in range(20):
        manager.remember("session", "user", f"unrelated message {index}")
        manager.remember("session", "assistant", "acknowledged")
    manager.remember("session", "user", "We decided to ship the Aurora dashboard")

    snapshot = manager.snapshot("session", "Continue with this project")

    assert "TASK" in snapshot.intent
    assert "active_task" in snapshot.references
    assert "Aurora dashboard" in snapshot.references["active_task"]


def test_multi_agent_team_selects_specialist_lanes():
    team = MultiAgentTeam()
    assert team.plan("debug this Python test").lane == "coding"
    assert team.plan("research the evidence").lane == "research"
    assert team.plan("plan the architecture").lane == "strategy"
    assert team.plan("hello").lane == "general"


def test_research_context_is_only_added_for_research_intent():
    rag = LocalKnowledgeRAG()
    rag.ingest_text("Aurora uses local retrieval for project memory.", source="architecture")
    ChatWebHandler.rag = rag

    evidence = ChatWebHandler._knowledge_context("research Aurora retrieval", ("RESEARCH",))
    ordinary = ChatWebHandler._knowledge_context("hello", ("CONVERSATION",))

    assert "Aurora" in evidence
    assert ordinary == ""
