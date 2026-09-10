"""Demo runner for FUTURE-50 local CLI smoke tests.

Run with:
    python demo.py
"""

from future50.app import Future50App


def main():
    tasks = [
        "research learning",
        "code python debug test",
        "plan reasoning strategy",
    ]

    for task in tasks:
        app = Future50App(task=task, autonomy="level_2")
        print(f"\nTASK: {task}")
        print(app.run())


if __name__ == "__main__":
    main()
