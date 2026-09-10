import tkinter as tk
import threading
import traceback

from future50.interface.gui import Future50DesktopGUI


def main():
    try:
        gui = Future50DesktopGUI()
        gui.root = tk.Tk()
        gui.root.title("FUTURE-50 | Local Intelligence OS")
        gui.root.geometry("1280x760")
        gui.root.minsize(1100, 640)
        gui.root.configure(bg="#eef4f8")
        gui._apply_theme()
        gui._build_ui()
        gui.root.update()

        def close_root():
            try:
                gui.root.destroy()
            except Exception as exc:
                print("close error:", exc)

        threading.Timer(0.5, close_root).start()
        gui.root.mainloop()
        print("gui loop ok")
    except Exception:
        traceback.print_exc()
        print("gui failed")


if __name__ == "__main__":
    main()
