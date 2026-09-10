"""Command-line entry point for FUTURE-50.

Local-first, web-free laptop use is the default interface.
"""

import argparse

from .app import Future50App
from .interface.cli import Future50CLI
from .interface.desktop import Future50DesktopShell
from .interface.gui import launch_gui


def main():
    parser = argparse.ArgumentParser(description="FUTURE-50 CLI")
    parser.add_argument("--task", default="research", help="Task type or user request")
    parser.add_argument("--autonomy", default="level_2", help="Autonomy level: level_0 to level_5")
    parser.add_argument("--interactive", action="store_true", help="Start a local interactive CLI loop")
    parser.add_argument("--desktop", action="store_true", help="Launch a local desktop-style terminal dashboard")
    parser.add_argument("--gui", action="store_true", help="Launch a local Tkinter desktop GUI")
    args = parser.parse_args()

    if args.gui:
        launch_gui()
        return

    if args.desktop:
        Future50DesktopShell().run()
        return

    if args.interactive:
        Future50CLI().interactive_loop()
        return

    app = Future50App(task=args.task, autonomy=args.autonomy)
    print(app.run())


if __name__ == "__main__":
    main()
