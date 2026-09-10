"""Local desktop-style terminal dashboard shell for FUTURE-50.

This file gives the project a software-like screen layout in a pure local CLI
workflow. It intentionally avoids any web server, internet, or paid service.
"""

from dataclasses import dataclass

from ..core.chat import Future50Chat
from ..core.model_router import ModelRouter
from ..memory.memory import InMemoryMemory
from ..knowledge.knowledge import KnowledgeBase
from ..agents.specialized import AgentRegistry
from ..plugins.registry import PluginRegistry
from ..workspace.project import ProjectWorkspace


@dataclass
class DesktopMenu:
    title: str
    action: str


class Future50DesktopShell:
    """Local command-line software dashboard shell."""

    def __init__(self):
        self.chat = Future50Chat()
        self.router = ModelRouter()
        self.memory = InMemoryMemory()
        self.knowledge = KnowledgeBase()
        self.agents = AgentRegistry()
        self.plugins = PluginRegistry()
        self.workspace = ProjectWorkspace(root=".")
        self.commands = [
            DesktopMenu("chat", "chat"),
            DesktopMenu("model route", "route"),
            DesktopMenu("memory", "memory"),
            DesktopMenu("knowledge", "knowledge"),
            DesktopMenu("plugins", "plugins"),
            DesktopMenu("workspace", "workspace"),
            DesktopMenu("exit", "exit"),
        ]

    def render_header(self) -> None:
        print("\n============================================")
        print("FUTURE-50 LOCAL DESKTOP SHELL")
        print("============================================")
        print("MODE: LOCAL-ONLY CLI")
        print("MODEL: future50-router")
        print("AUTONOMY: LEVEL_2")
        print("============================================")

    def render_menu(self) -> None:
        print("\nAVAILABLE MODULES")
        for index, menu in enumerate(self.commands, start=1):
            print(f"[{index}] {menu.title}")

    def route_task(self, task: str) -> str:
        model = self.router.route(task)
        response = self.chat.generate("user", task, model=model)
        return f"Route: {model.role.value}\n{response.text}"

    def dashboard(self, task: str = "research") -> None:
        self.render_header()
        self.render_menu()
        print("\nCURRENT TASK:", task)
        print("LOCAL MEMORY RECORDS:", len(self.memory.records))
        print("LOCAL KNOWLEDGE RECORDS:", len(self.knowledge.records))
        print("SPECIALIZED AGENTS:", len(self.agents.profiles))
        print("PLUGIN REGISTRATIONS:", len(self.plugins.plugins))
        print("WORKSPACE PROJECTS:", ", ".join(self.workspace.projects.keys()) or "none")

    def run(self) -> None:
        self.dashboard()
        while True:
            try:
                choice = input("\nfuture50-shell> ").strip().lower()
            except EOFError:
                print("\nLocal shell closed.")
                break

            if choice in {"exit", "quit", "bye", "q"}:
                print("FUTURE-50 shell closed.")
                break

            if choice == "1" or choice == "chat":
                task = input("task> ").strip()
                if not task:
                    print("No task entered.")
                    continue
                print(self.route_task(task))
            elif choice == "2" or choice == "route":
                task = input("route task> ").strip()
                if not task:
                    print("No route task entered.")
                    continue
                model = self.router.route(task)
                print(f"Selected model role: {model.role.value}")
            elif choice == "3" or choice == "memory":
                print("Memory records:", len(self.memory.records))
                for key, record in self.memory.records.items():
                    print(f"- {key}: {record.value}")
            elif choice == "4" or choice == "knowledge":
                print("Knowledge records:", len(self.knowledge.records))
                for record in self.knowledge.records:
                    print(f"- {record.topic}: {record.body[:60]}")
            elif choice == "5" or choice == "plugins":
                print("Plugins:", len(self.plugins.plugins))
                for plugin in self.plugins.plugins:
                    print(f"- {plugin.name} {plugin.version}")
            elif choice == "6" or choice == "workspace":
                print("Workspace projects:")
                for project in self.workspace.list_projects():
                    print(f"- {project.name}: {project.path}")
            else:
                print("Unknown command. Choose from the screen menu.")
            self.dashboard()
