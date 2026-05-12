import tkinter as tk
from tkinter import ttk
import threading
import time

from plagiarism_checker import get_model
import main_app


def show_loading_screen():
    splash = tk.Tk()
    splash.title("Loading Pattern Plagiarism Checker")
    splash.geometry("360x140")
    splash.configure(bg="#1e1e1e")

    label = tk.Label(
        splash,
        text="Loading Pattern Plagiarism Checker…",
        bg="#1e1e1e",
        fg="white",
        font=("Segoe UI", 12)
    )
    label.pack(pady=20)

    progress = ttk.Progressbar(splash, mode="indeterminate", length=260)
    progress.pack(pady=5)
    progress.start(10)

    # Start model loading in background
    threading.Thread(target=load_model, args=(splash,), daemon=True).start()

    splash.mainloop()


def load_model(splash_window):
    print("Loading model...")
    get_model()
    print("Model loaded.")

    # Close splash on main thread
    splash_window.after(0, lambda: finish_loading(splash_window))


def finish_loading(splash_window):
    splash_window.destroy()
    print("Launching GUI...")

    # Launch GUI on main thread
    main_app.start_gui()


if __name__ == "__main__":
    show_loading_screen()
