from future50.cognition.planner import PlanningEngine
from future50.plugins.registry import PluginRegistry
from future50.workspace.project import ProjectWorkspace


def test_planning_engine_creates_hierarchical_goal_node():
    engine = PlanningEngine()
    goal = engine.decompose("mission", "objective")
    assert goal.mission == "mission"
    assert goal.objective == "objective"
    assert goal.action == "observe"


def test_plugin_registry_registers_plugins():
    registry = PluginRegistry()
    plugin = registry.register("vision", capabilities=["image"])
    assert plugin.name == "vision"
    assert registry.list_plugins()[0].name == "vision"


def test_project_workspace_creates_projects():
    workspace = ProjectWorkspace(root=".")
    project = workspace.create_project("demo", "example")
    assert project.name == "demo"
    assert "demo" in workspace.projects
