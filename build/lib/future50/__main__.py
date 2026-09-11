"""Command-line entry point for the FUTURE-50 local web workspace."""

import argparse

from .app import Future50App
from .interface.cli import Future50CLI
from .web import run_web_app


def main():
    parser = argparse.ArgumentParser(description="FUTURE-50 CLI")
    parser.add_argument("--task", default="research", help="Task type or user request")
    parser.add_argument("--autonomy", default="level_2", help="Autonomy level: level_0 to level_5")
    parser.add_argument("--interactive", action="store_true", help="Start a local interactive CLI loop")
    parser.add_argument("--chat", action="store_true", help="Launch the premium local web chat")
    parser.add_argument("--gui", action="store_true", help="Compatibility alias for the local web chat")
    parser.add_argument("--desktop", action="store_true", help="Compatibility alias for the local web chat")
    parser.add_argument("--host", default="127.0.0.1", help="Web host")
    parser.add_argument("--port", default=8765, type=int, help="Web port")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser automatically")
    args = parser.parse_args()

    if args.gui or args.chat or args.desktop:
        run_web_app(args.host, args.port, open_browser=not args.no_browser)
        return

    if args.interactive:
        Future50CLI().interactive_loop()
        return

    run_web_app(args.host, args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
