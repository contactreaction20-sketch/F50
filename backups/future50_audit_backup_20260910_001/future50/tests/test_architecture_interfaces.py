from future50.cognition.reasoning import ReasoningEngine
from future50.self_improvement.lab import SelfImprovementLab
from future50.security.audit import AuditLog
from future50.tools.filesystem import FilesystemTool


def test_reasoning_engine_supports_simple_plan():
    engine = ReasoningEngine()
    result = engine.plan("build feature")
    assert result.goal == "build feature"
    assert "observe" in result.plan


def test_self_improvement_lab_records_experiment():
    lab = SelfImprovementLab()
    record = lab.create_record(
        experiment_id="exp-1",
        parent_version="v0.1",
        change_description="local improvement",
        expected_benefit="better planning",
        test_results="pass",
        benchmark_results="fast",
        regression_results="clean",
        final_decision="accept",
    )
    assert record.experiment_id == "exp-1"
    assert lab.records[-1].final_decision == "accept"


def test_audit_log_records_event():
    log = AuditLog()
    event = log.record("boot")
    assert event.event == "boot"


def test_filesystem_tool_creates_and_reads_file(tmp_path):
    tool = FilesystemTool(base_path=str(tmp_path))
    path = tool.write_text("note.txt", "hello")
    assert path.endswith("note.txt")
    assert tool.read_text("note.txt") == "hello"
