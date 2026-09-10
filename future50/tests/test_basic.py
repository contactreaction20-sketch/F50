import pytest

from future50.core.chat import Future50Chat
from future50.core.model_router import ModelRouter, ModelRole, LocalModel
from future50.core.permissions import PermissionLevel, PermissionManager
from future50.core.autonomy import AutonomyLevel
from future50.core.system import Future50Core
from future50.inference.providers import LocalOllamaProvider


def test_local_model_infer_returns_provider_response_without_placeholder_route(monkeypatch):
    model = LocalModel("future50-coding", ModelRole.CODING)
    monkeypatch.setattr("future50.core.model_router.model_provider.generate", lambda prompt, model=None, system=None: "Python issue fixed locally.")

    reply = model.infer("debug python bug")

    assert reply == "Python issue fixed locally."
    assert "I received your request" not in reply
    assert "routed it to the" not in reply


def test_local_model_infer_reports_provider_failure_cleanly_without_route_fallback(monkeypatch):
    model = LocalModel("future50-coding", ModelRole.CODING)
    monkeypatch.setattr("future50.core.model_router.model_provider.generate", lambda prompt, model=None, system=None: "Local model inference failed: provider unavailable")

    reply = model.infer("debug python bug")

    assert "Local model inference failed" in reply
    assert "I received your request" not in reply
    assert "routed it to the" not in reply


def test_provider_builds_same_language_system_instruction_for_hindi_prompt():
    provider = LocalOllamaProvider(model="qwen2.5:7b-instruct-q4_K_M")
    instruction = provider._same_language_instruction("namaste, aap kaise ho?")
    assert "Hindi" in instruction or "Hinglish" in instruction or "same language" in instruction.lower()


def test_local_model_infer_passes_same_language_system_prompt(monkeypatch):
    provider = LocalOllamaProvider(model="qwen2.5:7b-instruct-q4_K_M")
    calls = {}

    def fake_generate(prompt, model=None, system=None):
        calls['prompt'] = prompt
        calls['model'] = model
        calls['system'] = system
        return "Namaste, aap kaise hain?"

    monkeypatch.setattr("future50.core.model_router.model_provider", provider)
    monkeypatch.setattr(provider, "generate", fake_generate)

    reply = LocalModel("future50-coding", ModelRole.CODING).infer("namaste, aap kaise ho?")

    assert reply == "Namaste, aap kaise hain?"
    assert calls['prompt'] == "namaste, aap kaise ho?"
    assert calls['model'] == "qwen2.5:7b-instruct-q4_K_M"
    assert calls['system'] and "same language" in calls['system'].lower()


def test_router_routes_coding_tasks_to_coding_model():
    router = ModelRouter()
    model = router.route("debug python bug")
    assert model.role == ModelRole.CODING


def test_chat_generates_message():
    chat = Future50Chat()
    message = chat.generate("user", "hello")
    assert message.role == "assistant"
    assert message.text == "hello"


def test_permission_manager_gate():
    manager = PermissionManager()
    assert manager.can(PermissionLevel.READ)
    assert not manager.can(PermissionLevel.NETWORK)


def test_autonomy_from_string_supports_level_2():
    assert AutonomyLevel.from_string("level_2") == AutonomyLevel.LEVEL_2


def test_core_routes_memory_and_knowledge_reference_exist():
    core = Future50Core()
    assert core.memory is not None
    assert core.knowledge is not None
    assert core.model_router.route("code") is not None
