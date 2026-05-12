import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import os

from plagiarism_checker import compare_files, compare_file_to_folder
from extract_text import SUPPORTED_EXTENSIONS


# ============================================================
#   THEMES (DARK / LIGHT)
# ============================================================

THEMES = {
    "dark": {
        "bg": "#1e1e1e",
        "fg": "white",
        "button_bg": "#3a3a3a",
        "button_fg": "white",
        "button_active_bg": "#575757",
        "button_active_fg": "white",
        "frame_bg": "#1e1e1e",
        "textbox_bg": "#2b2b2b",
        "textbox_fg": "white",
    },
    "light": {
        "bg": "#f2f2f2",
        "fg": "black",
        "button_bg": "#e0e0e0",
        "button_fg": "black",
        "button_active_bg": "#c8c8c8",
        "button_active_fg": "black",
        "frame_bg": "#f2f2f2",
        "textbox_bg": "white",
        "textbox_fg": "black",
    }
}


# ============================================================
#   START GUI
# ============================================================

def start_gui():
    print("START_GUI CALLED")

    root = tk.Tk()
    root.title("Pattern Plagiarism Checker")
    root.geometry("860x840")

    current_theme = {"mode": "dark"}

    selected_file1 = None
    selected_file2 = None
    selected_folder = None

    file_mode = tk.StringVar(value="loose")
    folder_mode = tk.StringVar(value="loose")

    # Progress bar styles
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Green.Horizontal.TProgressbar", troughcolor="#2b2b2b", background="#4caf50")
    style.configure("Yellow.Horizontal.TProgressbar", troughcolor="#2b2b2b", background="#ffb300")
    style.configure("Red.Horizontal.TProgressbar", troughcolor="#2b2b2b", background="#f44336")

    # ============================================================
    #   THEME APPLICATION
    # ============================================================

    def apply_theme():
        theme = THEMES[current_theme["mode"]]
        root.configure(bg=theme["bg"])

        def update_widget(widget):
            cls = widget.__class__.__name__

            if cls in ("Frame", "LabelFrame"):
                widget.configure(bg=theme["frame_bg"])
            elif cls == "Label":
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            elif cls == "Button":
                widget.configure(
                    bg=theme["button_bg"],
                    fg=theme["button_fg"],
                    activebackground=theme["button_active_bg"],
                    activeforeground=theme["button_active_fg"],
                )
            elif cls == "Text":
                widget.configure(
                    bg=theme["textbox_bg"],
                    fg=theme["textbox_fg"],
                    insertbackground=theme["fg"]
                )

            for child in widget.winfo_children():
                update_widget(child)

        update_widget(root)

    def toggle_theme():
        current_theme["mode"] = "light" if current_theme["mode"] == "dark" else "dark"
        apply_theme()

    # ============================================================
    #   LOADING POPUP
    # ============================================================

    def show_loading_popup():
        popup = tk.Toplevel(root)
        popup.title("Processing")
        popup.geometry("300x120")
        popup.resizable(False, False)
        popup.configure(bg=THEMES[current_theme["mode"]]["bg"])
        popup.grab_set()

        label = tk.Label(
            popup,
            text="Analyzing similarity…\nPlease wait.",
            bg=THEMES[current_theme["mode"]]["bg"],
            fg=THEMES[current_theme["mode"]]["fg"],
            font=("Segoe UI", 11)
        )
        label.pack(pady=15)

        bar = ttk.Progressbar(popup, mode="indeterminate", length=220)
        bar.pack(pady=5)
        bar.start(10)

        return popup

    # ============================================================
    #   HELPERS
    # ============================================================

    def make_button(text, command, parent):
        theme = THEMES[current_theme["mode"]]
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=theme["button_bg"],
            fg=theme["button_fg"],
            activebackground=theme["button_active_bg"],
            activeforeground=theme["button_active_fg"],
            relief="flat",
            padx=10,
            pady=5,
            font=("Segoe UI", 10)
        )

    def supported_filetypes_filter():
        exts = sorted(list(SUPPORTED_EXTENSIONS))
        patterns = " ".join(f"*{e}" for e in exts)
        return [("Supported files", patterns)]

    # ============================================================
    #   FILE SELECTORS
    # ============================================================

    def select_file1():
        nonlocal selected_file1
        path = filedialog.askopenfilename(filetypes=supported_filetypes_filter())
        if path:
            selected_file1 = path
            lbl_file1.config(text=f"File 1: {os.path.basename(selected_file1)}")

    def select_file2():
        nonlocal selected_file2
        path = filedialog.askopenfilename(filetypes=supported_filetypes_filter())
        if path:
            selected_file2 = path
            lbl_file2.config(text=f"File 2: {os.path.basename(selected_file2)}")

    def select_folder():
        nonlocal selected_folder
        folder = filedialog.askdirectory()
        if folder:
            selected_folder = folder
            lbl_folder.config(text=f"Folder: {os.path.basename(selected_folder)}")

    # ============================================================
    #   CONFIDENCE METER
    # ============================================================

    def similarity_category(score: float):
        if score < 0.20:
            return "Low similarity", "#4caf50", "Green.Horizontal.TProgressbar"
        elif score < 0.60:
            return "Medium similarity", "#ffb300", "Yellow.Horizontal.TProgressbar"
        else:
            return "High similarity", "#f44336", "Red.Horizontal.TProgressbar"

    def update_confidence(score: float, context_text=""):
        percentage = score * 100
        label_text, color, style_name = similarity_category(score)

        confidence_label.config(
            text=f"{context_text}Similarity: {percentage:.1f}% — {label_text}",
            fg=color
        )
        confidence_bar.config(style=style_name)
        confidence_bar["value"] = percentage
        confidence_pct_label.config(text=f"{percentage:.1f}%")

    def reset_confidence():
        confidence_label.config(text="No similarity data yet")
        confidence_bar["value"] = 0
        confidence_pct_label.config(text="0.0%")

    # ============================================================
    #   RUN COMPARISONS
    # ============================================================

    def run_file_compare():
        if not selected_file1 or not selected_file2:
            messagebox.showerror("Error", "Please select both files.")
            return

        popup = show_loading_popup()

        def task():
            mode = file_mode.get()
            similarity = compare_files(selected_file1, selected_file2, mode=mode)
            popup.destroy()

            percentage = similarity * 100
            label_text, _, _ = similarity_category(similarity)

            result_box.config(state="normal")
            result_box.delete("1.0", tk.END)
            result_box.insert(
                tk.END,
                f"File vs File Similarity\n\n"
                f"Mode: {mode.capitalize()}\n\n"
                f"File 1: {os.path.basename(selected_file1)}\n"
                f"File 2: {os.path.basename(selected_file2)}\n\n"
                f"Similarity percentage: {percentage:.1f}%\n"
                f"Category: {label_text}\n"
            )
            result_box.config(state="disabled")

            update_confidence(similarity, "File vs File — ")

        threading.Thread(target=task, daemon=True).start()

    def run_folder_compare():
        if not selected_file1 or not selected_folder:
            messagebox.showerror("Error", "Please select a base file and a folder.")
            return

        popup = show_loading_popup()

        def task():
            mode = folder_mode.get()
            results = compare_file_to_folder(selected_file1, selected_folder, mode=mode)
            popup.destroy()

            result_box.config(state="normal")
            result_box.delete("1.0", tk.END)

            result_box.insert(
                tk.END,
                f"File vs Folder Similarity\n\n"
                f"Mode: {mode.capitalize()}\n\n"
                f"Base file: {os.path.basename(selected_file1)}\n"
                f"Folder: {selected_folder}\n\n"
            )

            if not results:
                result_box.insert(tk.END, "No supported files found.\n")
                result_box.config(state="disabled")
                reset_confidence()
                return

            for file, score in results:
                percentage = score * 100
                label_text, _, _ = similarity_category(score)
                result_box.insert(tk.END, f"{file}: {percentage:.1f}% — {label_text}\n")

            result_box.config(state="disabled")

            top_file, top_score = results[0]
            update_confidence(top_score, f"Top match ({top_file}) — ")

        threading.Thread(target=task, daemon=True).start()

    # ============================================================
    #   UI LAYOUT
    # ============================================================

    title_label = tk.Label(
        root,
        text="Pattern Plagiarism Checker",
        font=("Segoe UI", 16, "bold")
    )
    title_label.pack(pady=15)

    theme_button = tk.Button(
        root,
        text="Toggle Theme",
        command=toggle_theme,
        font=("Segoe UI", 10),
        relief="flat",
        padx=10,
        pady=5
    )
    theme_button.pack(pady=5)

    # File vs File
    file_frame = tk.LabelFrame(root, text="Compare File vs File", padx=10, pady=10, font=("Segoe UI", 12, "bold"))
    file_frame.pack(pady=10, fill="x")

    mode_frame_file = tk.Frame(file_frame)
    mode_frame_file.pack(anchor="w")

    tk.Label(mode_frame_file, text="Mode:", font=("Segoe UI", 9, "bold")).pack(side="left")
    tk.Radiobutton(mode_frame_file, text="Strict", variable=file_mode, value="strict").pack(side="left")
    tk.Radiobutton(mode_frame_file, text="Loose", variable=file_mode, value="loose").pack(side="left")

    btn_file1 = make_button("Select File 1", select_file1, file_frame)
    btn_file1.pack(pady=5)
    lbl_file1 = tk.Label(file_frame, text="File 1: None")
    lbl_file1.pack()

    btn_file2 = make_button("Select File 2", select_file2, file_frame)
    btn_file2.pack(pady=5)
    lbl_file2 = tk.Label(file_frame, text="File 2: None")
    lbl_file2.pack()

    btn_compare_files = make_button("Run File vs File Comparison", run_file_compare, file_frame)
    btn_compare_files.pack(pady=10)

    # File vs Folder
    folder_frame = tk.LabelFrame(root, text="Compare File vs Folder", padx=10, pady=10, font=("Segoe UI", 12, "bold"))
    folder_frame.pack(pady=10, fill="x")

    mode_frame_folder = tk.Frame(folder_frame)
    mode_frame_folder.pack(anchor="w")

    tk.Label(mode_frame_folder, text="Mode:", font=("Segoe UI", 9, "bold")).pack(side="left")
    tk.Radiobutton(mode_frame_folder, text="Strict", variable=folder_mode, value="strict").pack(side="left")
    tk.Radiobutton(mode_frame_folder, text="Loose", variable=folder_mode, value="loose").pack(side="left")

    btn_base_file = make_button("Select Base File", select_file1, folder_frame)
    btn_base_file.pack(pady=5)

    btn_folder = make_button("Select Folder", select_folder, folder_frame)
    btn_folder.pack(pady=5)

    lbl_folder = tk.Label(folder_frame, text="Folder: None")
    lbl_folder.pack()

    btn_folder_compare = make_button("Run File vs Folder Comparison", run_folder_compare, folder_frame)
    btn_folder_compare.pack(pady=10)

    # Results box
    result_box = tk.Text(root, height=14, width=90, relief="flat")
    result_box.pack(pady=20)
    result_box.config(state="disabled")

    # Confidence meter
    confidence_frame = tk.Frame(root)
    confidence_frame.pack(pady=10, fill="x")

    confidence_label = tk.Label(confidence_frame, text="No similarity data yet", font=("Segoe UI", 10, "bold"))
    confidence_label.pack(anchor="w")

    bar_container = tk.Frame(confidence_frame)
    bar_container.pack(fill="x")

    confidence_bar = ttk.Progressbar(bar_container, orient="horizontal", mode="determinate", length=500, maximum=100)
    confidence_bar.pack(side="left", padx=(0, 10))

    confidence_pct_label = tk.Label(bar_container, text="0.0%", font=("Segoe UI", 10))
    confidence_pct_label.pack(side="left")

    apply_theme()
    root.mainloop()
