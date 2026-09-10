"""Premium local desktop GUI shell for FUTURE-50.

This is a full-screen professional software-style workstation UI built from
standard Python/Tkinter primitives without a web server or browser.
"""

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable

from ..core.chat import Future50Chat
from ..core.model_router import ModelRouter
from ..memory.memory import InMemoryMemory
from ..knowledge.knowledge import KnowledgeBase
from ..agents.specialized import AgentRegistry
from ..plugins.registry import PluginRegistry
from ..workspace.project import ProjectWorkspace


class Future50DesktopGUI:
    """Premium software-like desktop interface for FUTURE-50."""

    def __init__(self):
        self.chat = Future50Chat()
        self.router = ModelRouter()
        self.memory = InMemoryMemory()
        self.knowledge = KnowledgeBase()
        self.agents = AgentRegistry()
        self.plugins = PluginRegistry()
        self.workspace = ProjectWorkspace(root=".")
        self.root = None
        self.chat_log = None
        self.input_box = None
        self.status = None
        self.summary = None
        self.active_menu = None

    def start(self) -> None:
        """Create and run a premium Tkinter desktop window locally."""
        try:
            self.root = tk.Tk()
            self.root.title("FUTURE-50 | Local Intelligence OS")
            self.root.geometry("1280x760")
            self.root.minsize(1100, 640)
            self.root.configure(bg="#eef4f8")
            self._apply_theme()
            self._build_ui()
            self.root.mainloop()
        except Exception as exc:
            print("GUI backend unavailable; falling back to console shell:", exc)
            self._fall_back_console()

    def _apply_theme(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#0c1b2b", background="#eef4f8")
        style.configure("Nav.TButton", font=("Segoe UI", 10, "bold"), foreground="#eaf2f8", background="#08192b")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), foreground="#10263d", background="#b0eecc")

    def _build_ui(self) -> None:
        self.root.configure(bg="#eef4f8")

        # Header row
        header = tk.Frame(self.root, bg="#071627", height=76)
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Label(header, text="FUTURE-50", font=("Segoe UI", 26, "bold"), bg="#071627", fg="#dffbff")
        brand.place(x=30, y=12)

        brand_sub = tk.Label(header, text="LOCAL INTELLIGENCE OS", font=("Segoe UI", 10, "bold"), bg="#071627", fg="#9ed8ff")
        brand_sub.place(x=34, y=50)

        status_pill = tk.Label(header, text="ONLINE // LOCAL MODE", font=("Segoe UI", 10, "bold"), bg="#071627", fg="#9dffc8")
        status_pill.place(x=1020, y=24)

        # Main body layout
        body = tk.Frame(self.root, bg="#eef4f8")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        # Sidebar
        sidebar = tk.Frame(body, bg="#10233a", width=250)
        sidebar.pack(side="left", fill="y", padx=(0, 14))
        sidebar.pack_propagate(False)

        sidebar_title = tk.Label(sidebar, text="OPERATIONS", bg="#10233a", fg="#dffbff", font=("Segoe UI", 12, "bold"))
        sidebar_title.pack(anchor="w", padx=22, pady=(24, 12))

        menu_items = [
            ("Chat", "chat"),
            ("Route Model", "route"),
            ("Memory", "memory"),
            ("Knowledge", "knowledge"),
            ("Plugins", "plugins"),
            ("Workspace", "workspace"),
            ("Exit", "exit"),
        ]

        self.active_menu = "chat"
        for index, (label, action) in enumerate(menu_items, start=1):
            btn = tk.Button(
                sidebar,
                text=f"{index}. {label}",
                fg="#eaf7fb",
                bg="#10233a",
                activebackground="#1e496e",
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                padx=14,
                pady=12,
                anchor="w",
                font=("Segoe UI", 10, "bold"),
                command=lambda a=action: self.on_menu(a),
            )
            btn.pack(fill="x", padx=12, pady=5)

        # Content area
        content = tk.Frame(body, bg="#eef4f8")
        content.pack(side="left", fill="both", expand=True)

        # top panel rows
        top_grid = tk.Frame(content, bg="#eef4f8")
        top_grid.pack(fill="x", pady=(0, 10))

        self.status = tk.Label(top_grid, text="chat ready", bg="#eef4f8", fg="#173d5b", font=("Segoe UI", 11, "bold"), anchor="w")
        self.status.pack(side="left", fill="x", expand=True)

        route_label = tk.Label(top_grid, text="Model: future50-router", bg="#eef4f8", fg="#496c7f", font=("Segoe UI", 10, "bold"))
        route_label.pack(side="right", padx=(0, 6))

        # chat area
        card = tk.Frame(content, bg="#ffffff", bd=1, relief="flat")
        card.pack(fill="both", expand=True)

        self.chat_log = scrolledtext.ScrolledText(
            card,
            height=22,
            wrap="word",
            state="disabled",
            bg="#07111f",
            fg="#dffbff",
            insertbackground="#dffbff",
            font=("Segoe UI", 11),
            padx=12,
            pady=12,
        )
        self.chat_log.pack(fill="both", expand=True, padx=10, pady=(10, 8))

        input_row = tk.Frame(card, bg="#ffffff")
        input_row.pack(fill="x", padx=10, pady=(0, 10))

        self.input_box = tk.Entry(input_row, font=("Segoe UI", 11), bg="#eef4f8", fg="#07111f", relief="flat", bd=1)
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", lambda event: self.on_send())

        send_button = tk.Button(input_row, text="SEND", bg="#173d5b", fg="#dffbff", relief="flat", font=("Segoe UI", 10, "bold"), command=self.on_send)
        send_button.pack(side="right", padx=(0, 2))

        # workspace summary
        footer = tk.Frame(content, bg="#eef4f8")
        footer.pack(fill="x", pady=(8, 0))
        self.summary = tk.Label(
            footer,
            text=f"Projects: {', '.join(self.workspace.projects.keys()) or 'none'} | Agents: {len(self.agents.profiles)} | Plugins: {len(self.plugins.plugins)}",
            bg="#eef4f8",
            fg="#24415e",
            justify="left",
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        )
        self.summary.pack(fill="x")

    def on_menu(self, action: str) -> None:
        if action == "chat":
            self.status.configure(text="chat ready")
            self._append_chat("system: chat workspace online")
        elif action == "route":
            self.status.configure(text="route model selected")
            self._append_chat("system: model router online")
        elif action == "memory":
            self.status.configure(text=f"memory records: {len(self.memory.records)}")
            self._append_chat("system: memory workspace online")
        elif action == "knowledge":
            self.status.configure(text=f"knowledge records: {len(self.knowledge.records)}")
            self._append_chat("system: knowledge workspace online")
        elif action == "plugins":
            self.status.configure(text=f"plugin registrations: {len(self.plugins.plugins)}")
            self._append_chat("system: plugin registry online")
        elif action == "workspace":
            self.status.configure(text="workspace selected")
            self._append_chat("system: workspace directory online")
        elif action == "exit":
            if self.root:
                self.root.destroy()

    def on_send(self) -> None:
        task = self.input_box.get().strip()
        if not task:
            return

        self._append_chat(f"user: {task}")
        self.status.configure(text="thinking...")

        # Keep the UI responsive if a real Tk root exists. If the object is
        # constructed for testing or for a non-GUI use case, stay synchronous
        # and return the assistant reply in the same call stack.
        if self.root is None:
            model = self.router.route(task)
            response = self.chat.generate("user", task, model=model)
            self._append_chat(f"assistant: {response.text}")
            self.status.configure(text=f"route: {model.role.value}")
            if self.input_box:
                try:
                    self.input_box.delete(0, tk.END)
                except Exception:
                    pass
            return

        def run_generation() -> None:
            model = self.router.route(task)
            try:
                response = self.chat.generate("user", task, model=model)
                text = response.text
            except Exception as exc:
                text = f"Local model inference failed: {exc}"

            def ui_update():
                self._append_chat(f"assistant: {text}")
                self.status.configure(text=f"route: {model.role.value}")
                if self.input_box:
                    try:
                        self.input_box.delete(0, tk.END)
                    except Exception:
                        pass

            self.root.after(0, ui_update)

        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()

    def _append_chat(self, text: str) -> None:
        if self.chat_log:
            self.chat_log.configure(state="normal")
            self.chat_log.insert(tk.END, text + "\n")
            self.chat_log.see(tk.END)
            self.chat_log.configure(state="disabled")

    def _fall_back_console(self) -> None:
        print("FUTURE-50 local GUI fallback started.")
        print("Use --interactive or --desktop for terminal CLI mode.")


def launch_gui() -> None:
    gui = Future50DesktopGUI()
    gui.start()
