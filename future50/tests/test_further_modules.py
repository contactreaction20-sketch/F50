from future50.agents.specialized import AgentRegistry
from future50.world_model.world_model import FactStatus, WorldModel
from future50.evaluation.evaluation import EvaluationEngine
from future50.scheduler.scheduler import TaskScheduler
from future50.database.database import LocalDatabase
from future50.monitoring.monitoring import MonitoringService
from future50.plugins.plugin import Plugin, PluginMetadata


def test_agent_registry_exposes_required_profiles():
    registry = AgentRegistry()
    names = {profile.name for profile in registry.list_profiles()}
    assert "Orchestrator" in names
    assert "Coder" in names
    assert "Self-Improvement Agent" in names


def test_world_model_tracks_statuses_and_confidence():
    model = WorldModel()
    fact = model.add_fact("core", "has", "local_model", status=FactStatus.KNOWN, confidence=0.90)
    assert fact.status == FactStatus.KNOWN
    assert fact.confidence == 0.90


def test_evaluation_engine_records_benchmark():
    engine = EvaluationEngine()
    result = engine.record_benchmark("router", "latency_ms", 12.5)
    assert result.metric == "latency_ms"


def test_scheduler_and_database_and_monitoring_stubs_work():
    scheduler = TaskScheduler()
    task = scheduler.create_task("learn", constraints=["local"])
    assert task.objective == "learn"

    db = LocalDatabase()
    row = db.put("memory", "key", "value")
    assert db.get("memory", "key").value == "value"

    monitor = MonitoringService()
    snapshot = monitor.sample(cpu=5.0, ram=6.0, disk=7.0)
    assert snapshot.cpu == 5.0
    assert snapshot.status == "nominal"


def test_plugin_metadata_is_exposed():
    plugin = Plugin(PluginMetadata("research", "0.1.0", ["knowledge"], ["read"]))
    assert plugin.describe().name == "research"
