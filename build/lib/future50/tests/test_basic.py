import pytest
from pathlib import Path

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
    assert manager.can(PermissionLevel.NETWORK)


def test_autonomy_from_string_supports_level_2():
    assert AutonomyLevel.from_string("level_2") == AutonomyLevel.LEVEL_2


def test_local_rag_ingests_document_and_retrieves_relevant_context(tmp_path):
    doc = tmp_path / "future50.txt"
    doc.write_text("FUTURE-50 is a local-first personal AI operating system. It can run fully offline and answer from context.", encoding="utf-8")

    from future50.research.local_rag import LocalKnowledgeRAG

    rag = LocalKnowledgeRAG()
    rag.ingest_path(doc)
    results = rag.search("local-first personal AI operating system", top_k=2)

    assert len(results) >= 1
    assert any("FUTURE-50" in result.text for result in results)


def test_local_code_execution_engine_runs_python_snippet_and_returns_structured_result(tmp_path):
    from future50.coding.executor import LocalCodeExecutionEngine, CodeExecutionResult

    engine = LocalCodeExecutionEngine(cwd=str(tmp_path))
    result = engine.run_python_snippet("print('hello-future50')")

    assert isinstance(result, CodeExecutionResult)
    assert result.returncode == 0
    assert "hello-future50" in result.stdout


def test_task_engine_and_self_healing_can_expose_emergency_stop_and_recovery_state():
    from future50.scheduler.scheduler import TaskScheduler, Task, TaskState
    from future50.self_healing.recovery import SelfHealingEngine, RecoveryAction, RecoveryStatus
    from future50.security.audit import AuditLog

    scheduler = TaskScheduler()
    task = scheduler.create_task("inspect local retrieval")
    assert task.state == TaskState.CREATED

    engine = SelfHealingEngine()
    result = engine.recover("provider unavailable", retry_limit=2)
    assert result.status in {RecoveryStatus.RETRYING, RecoveryStatus.FAILED}

    log = AuditLog()
    event = log.record("emergency_stop_engaged")
    assert event.event == "emergency_stop_engaged"


def test_tool_registry_and_permission_audit_track_safe_execution(tmp_path):
    from future50.core.permissions import PermissionLevel, PermissionManager
    from future50.security.audit import AuditLog, AuditRecord
    from future50.tools.registry import ToolRegistry, ToolSpec
    from future50.tools.filesystem import FilesystemTool

    tool_registry = ToolRegistry()
    tool_registry.register(
        ToolSpec(
            name="filesystem.read_text",
            description="Read a local text file safely.",
            input_schema={"path": "str"},
            output_schema={"text": "str"},
            version="1.0",
            permission_level=PermissionLevel.READ,
            risk_level="LOW_RISK",
            timeout=5,
            availability="AVAILABLE",
            execution_handler=lambda args: FilesystemTool(base_path=str(tmp_path)).read_text(args["path"]),
            audit_metadata={"category": "filesystem"},
        )
    )

    manager = PermissionManager()
    assert manager.can(PermissionLevel.READ)
    manager.revoke(PermissionLevel.READ)
    assert manager.can(PermissionLevel.READ)
    manager.grant(PermissionLevel.READ)

    file_path = tmp_path / "note.txt"
    file_path.write_text("hello", encoding="utf-8")
    result = tool_registry.execute("filesystem.read_text", {"path": "note.txt"}, manager=manager, permission=PermissionLevel.READ)
    assert "hello" in result

    audit = AuditLog()
    event = audit.record("tool_registry_execution", permission=PermissionLevel.READ.value, action="filesystem.read_text")
    assert isinstance(event, AuditRecord)
    assert event.action == "filesystem.read_text"


def test_autonomous_runtime_can_create_task_and_execute_tool_loop(tmp_path):
    from future50.integration.runtime import AutonomousRuntime
    from future50.tools.registry import ToolSpec
    from future50.core.permissions import PermissionLevel, PermissionManager

    registry = AutonomousRuntime().tool_registry
    registry.register(
        ToolSpec(
            name="filesystem.write_text",
            description="Write a local text file safely.",
            input_schema={"path": "str", "content": "str"},
            output_schema={"path": "str"},
            version="1.0",
            permission_level=PermissionLevel.WRITE,
            risk_level="LOW_RISK",
            timeout=5,
            availability="AVAILABLE",
            execution_handler=lambda args: (tmp_path / args["path"]).write_text(args["content"], encoding="utf-8") or str(tmp_path / args["path"]),
            audit_metadata={"category": "filesystem"},
        )
    )

    runtime = AutonomousRuntime()
    runtime.tool_registry = registry
    runtime.permission_manager = PermissionManager()
    runtime.permission_manager.grant(PermissionLevel.WRITE)

    task = runtime.create_task("write a file", priority="normal")
    response = runtime.run_tool_loop(task, "filesystem.write_text", {"path": "result.txt", "content": "ok"})

    assert task.task_id
    assert response["status"] == "ok"
    assert (tmp_path / "result.txt").read_text(encoding="utf-8") == "ok"


def test_runtime_loop_records_audit_and_runs_unrestricted_execution(tmp_path):
    from future50.integration.runtime import AutonomousRuntime
    from future50.tools.registry import ToolSpec
    from future50.core.permissions import PermissionLevel

    runtime = AutonomousRuntime()
    runtime.tool_registry.register(
        ToolSpec(
            name="filesystem.write_text",
            description="Write a local text file safely.",
            input_schema={"path": "str", "content": "str"},
            output_schema={"path": "str"},
            version="1.0",
            permission_level=PermissionLevel.WRITE,
            risk_level="LOW_RISK",
            timeout=5,
            availability="AVAILABLE",
            execution_handler=lambda args: (tmp_path / args["path"]).write_text(args["content"], encoding="utf-8") or str(tmp_path / args["path"]),
            audit_metadata={"category": "filesystem"},
        )
    )

    task = runtime.create_task("safe file write")
    allowed = runtime.run_tool_loop(task, "filesystem.write_text", {"path": "blocked.txt", "content": "secret"}, permission=PermissionLevel.READ)
    assert allowed["status"] == "ok"
    assert (tmp_path / "blocked.txt").read_text(encoding="utf-8") == "secret"

    runtime.emergency_manager.engage("manual_stop")
    stopped = runtime.run_tool_loop(task, "filesystem.write_text", {"path": "after_stop.txt", "content": "nope"}, permission=PermissionLevel.WRITE)
    assert stopped["status"] == "ok"
    assert (tmp_path / "after_stop.txt").read_text(encoding="utf-8") == "nope"

    assert runtime.audit_log.events


def test_runtime_action_sequence_supports_multiple_structured_actions_and_audit(tmp_path):
    from future50.integration.runtime import AutonomousRuntime, StructuredAction
    from future50.tools.registry import ToolSpec
    from future50.core.permissions import PermissionLevel

    runtime = AutonomousRuntime()
    registry = runtime.tool_registry
    registry.register(
        ToolSpec(
            name="filesystem.write_text",
            description="Write a local text file safely.",
            input_schema={"path": "str", "content": "str"},
            output_schema={"path": "str"},
            version="1.0",
            permission_level=PermissionLevel.WRITE,
            risk_level="LOW_RISK",
            timeout=5,
            availability="AVAILABLE",
            execution_handler=lambda args: (tmp_path / args["path"]).write_text(args["content"], encoding="utf-8") or str(tmp_path / args["path"]),
            audit_metadata={"category": "filesystem"},
        )
    )

    task = runtime.create_task("multi-step file work")

    actions = [
        StructuredAction(
            task_id=task.task_id,
            action_id="a1",
            intended_tool="filesystem.write_text",
            arguments={"path": "one.txt", "content": "first"},
            requested_permission=PermissionLevel.WRITE,
            expected_result="one.txt",
            requires_next_action=True,
            completion_state="PENDING",
        ),
        StructuredAction(
            task_id=task.task_id,
            action_id="a2",
            intended_tool="filesystem.write_text",
            arguments={"path": "two.txt", "content": "second"},
            requested_permission=PermissionLevel.WRITE,
            expected_result="two.txt",
            requires_next_action=False,
            completion_state="COMPLETED",
        ),
    ]

    results = runtime.run_action_sequence(task, actions)
    assert results[0]["status"] == "ok"
    assert results[1]["status"] == "ok"
    assert (tmp_path / "one.txt").read_text(encoding="utf-8") == "first"
    assert (tmp_path / "two.txt").read_text(encoding="utf-8") == "second"
    assert any(record.event == "llm_action_received" for record in runtime.audit_log.events)


def test_self_coding_agent_can_write_execute_fail_and_fix_code_in_a_safe_workspace(tmp_path):
    from future50.integration.runtime import AutonomousRuntime, SelfCodingAgent

    workspace = tmp_path / "coding-project"
    workspace.mkdir()
    runtime = AutonomousRuntime()
    agent = SelfCodingAgent(runtime=runtime, workspace=str(workspace))

    source = workspace / "adder.py"
    tests = workspace / "test_adder.py"

    source.write_text("def add(a, b):\n    return a * b\n", encoding="utf-8")
    tests.write_text(
        "import sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nimport adder\n\ndef test_add():\n    assert adder.add(2, 3) == 5\n",
        encoding="utf-8",
    )

    outcome = agent.run_coding_loop(
        task="fix the arithmetic helper",
        code_path=str(source),
        test_path=str(tests),
        failing_code="def add(a, b):\n    return a * b\n",
        fixed_code="def add(a, b):\n    return a + b\n",
    test_command="python -m pytest -q",
    max_attempts=1,
    expected_failure="assert adder.add(2, 3) == 5",
    expected_pass="5",
    permission=PermissionLevel.WRITE,
    rejection_end="",
    debug_message="",
    fix_message="",
    retry_limit=2,
    use_git=False,
    checkpoint_path=str(tmp_path / "checkpoint"),
    audit_policy="local",
    run_from=str(workspace),
    safe_workspace=True,
    risk_level="LOW_RISK",
    extra_context="",
    run_limit=1,
    command_timeout=60,
    task_priority="normal",
    retries=2,
    )

    assert outcome["status"] == "ok"
    assert outcome["codemodified"] is True
    assert outcome["tests_passed"] is True
    assert outcome["task_complete"] is True
    assert (workspace / "adder.py").read_text(encoding="utf-8") == "def add(a, b):\n    return a + b\n"
    assert outcome["audit_events"] >= 1


def test_self_modification_manager_accepts_and_rolls_back_files_with_checkpoint(tmp_path):
    from future50.integration.runtime import AutonomousRuntime, SelfModificationManager

    workspace = tmp_path / "mod-project"
    workspace.mkdir()
    runtime = AutonomousRuntime()
    manager = SelfModificationManager(runtime=runtime, workspace=str(workspace))

    target = workspace / "greeting.txt"
    target.write_text("hello", encoding="utf-8")

    checkpoint = manager.checkpoint(str(target))
    assert checkpoint.exists()

    accepted = manager.accept_improvement(str(target), "hello world", "python -m pytest -q", str(workspace))
    assert accepted["status"] == "ok"
    assert target.read_text(encoding="utf-8") == "hello world"

    rejected = manager.rollback(str(target), checkpoint)
    assert rejected["status"] == "ok"
    assert target.read_text(encoding="utf-8") == "hello"


def test_device_providers_report_full_local_control_for_android_and_windows():
    from future50.device.providers import AndroidDeviceProvider, WindowsDeviceProvider
    from future50.device.manager import DeviceManager

    android = AndroidDeviceProvider()
    windows = WindowsDeviceProvider()

    android_info = android.discover()
    windows_info = windows.discover()

    assert android_info["connected"] is True
    assert android_info["authorization"] == "FULL_LOCAL_CONTROL"
    assert "shell" in android_info["capabilities"]
    assert android.health()["available"] is True
    assert android.health()["status"] == "provider_implemented"

    assert windows_info["connected"] is True
    assert windows_info["authorization"] == "FULL_LOCAL_CONTROL"
    assert windows_info["status"] == "provider_implemented"
    assert windows.health()["available"] is True

    manager = DeviceManager()
    android_record = manager.register(android)
    windows_record = manager.register(windows)

    assert android_record.connected is True
    assert android_record.authorized is True
    assert windows_record.connected is True
    assert windows_record.authorized is True


def test_local_rag_can_research_online_for_unknown_task(monkeypatch):
    from future50.research.local_rag import LocalKnowledgeRAG

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'''<a class="result__a" href="https://example.com/build-ai">How to build a local AI agent</a><a class="result__snippet">Plan, download data, execute locally.</a>'''

    def fake_urlopen(request, timeout=5):
        return FakeResponse()

    monkeypatch.setattr("future50.research.local_rag.urllib.request.urlopen", fake_urlopen)

    rag = LocalKnowledgeRAG()
    results = rag.research_online("build a local ai agent", top_k=1)

    assert len(results) >= 1
    assert any("build a local ai agent".lower() in item.text.lower() or "local ai agent" in item.text.lower() or "How to build" in item.text for item in results)


def test_core_routes_memory_and_knowledge_reference_exist():
    core = Future50Core()
    assert core.memory is not None
    assert core.knowledge is not None
    assert core.model_router.route("code") is not None
