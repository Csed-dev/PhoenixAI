import os
import tkinter as tk
from tkinter import END, ttk, messagebox
from tkinter.scrolledtext import ScrolledText

import threading
import json

from name_checker import NameChecker

# ----------------------------------------
#   Beispiel-Variablen und -Funktionen
#   für die Pipeline-Schritte
# ----------------------------------------

class AnalysisPipelineStep:
    def __init__(self, name, function, *args, **kwargs):
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.status = "Pending"
        self.duration = None

    def run(self):
        try:
            self.status = "Running..."
            if self.function:
                self.function(*self.args, **self.kwargs)
            self.status = "✅ OK"
        except Exception as e:
            self.status = f"🔴 Failed: {e}"

class AnalysisPipeline:
    def __init__(self, treeview):
        self.steps = []
        self.current_step = 0
        self.treeview = treeview

    def add_step(self, name, function, *args, **kwargs):
        step = AnalysisPipelineStep(name, function, *args, **kwargs)
        self.steps.append(step)
        self.display_status()

    def display_status(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for idx, step in enumerate(self.steps, start=1):
            self.treeview.insert(
                "",
                "end",
                iid=str(idx),
                values=(step.status, step.name, self._display_args(step), "N/A")
            )

    def run_next_step(self):
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            step.run()
            self.display_status()
            self.current_step += 1
        else:
            messagebox.showinfo("Info", "Alle Analyseschritte sind abgeschlossen.")

    def reset(self):
        self.steps.clear()
        self.current_step = 0
        self.display_status()

    def _display_args(self, step):
        """Zeigt maximal die letzten Segmente des Dateipfades an."""
        if step.args:
            path = step.args[0]
            parts = path.split(os.sep)
            if len(parts) > 4:
                return os.path.join(*parts[-4:])
            return path
        return "N/A"

# Beispiel-Funktionen für die Actions
def run_script1(file_path):
    print(f"[Pipeline] Skript 1 läuft auf: {file_path}")

def run_script2(file_path):
    print(f"[Pipeline] Skript 2 läuft auf: {file_path}")

def run_name_checker(file_path):
    print(f"[Pipeline] NameChecker läuft auf: {file_path}")
    checker = NameChecker(file_path)
    checker.generate_report()
    checker.save_report("name_checker_report.md")

def run_script4(file_path):
    print(f"[Pipeline] Skript 4 läuft auf: {file_path}")

analysis_actions = {
    "Skript 1": run_script1,
    "Skript 2": run_script2,
    "Name Checker": run_name_checker,
    "Skript 4": run_script4
}

# ----------------------------------------
#   GUI analog zu gui_transform.py
# ----------------------------------------
back_history = []
forward_history = []
current_directory = os.getcwd()
selected_file = None

def list_directory_contents(directory):
    contents = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isdir(full_path):
            contents.append(f"{item}/")
        elif item.endswith(".py"):
            contents.append(item)
    return contents

def update_directory_list(directory, dir_listbox, dir_label, pipeline, add_to_history=True):
    global current_directory, back_history, forward_history

    if add_to_history:
        back_history.append(current_directory)

    if add_to_history and current_directory != directory:
        forward_history.clear()

    current_directory = directory
    dir_listbox.delete(0, END)
    contents = list_directory_contents(directory)
    for item in contents:
        dir_listbox.insert(END, item)
    dir_label.config(text=f"Aktuelles Verzeichnis: {directory}")
    pipeline.reset()

def navigate_up(dir_listbox, dir_label, pipeline):
    global current_directory
    parent_directory = os.path.dirname(current_directory)
    if parent_directory != current_directory:
        update_directory_list(parent_directory, dir_listbox, dir_label, pipeline)
    else:
        messagebox.showinfo("Info", "Sie befinden sich bereits im Wurzelverzeichnis.")

def navigate_back(dir_listbox, dir_label, pipeline):
    global back_history, current_directory, forward_history
    if back_history:
        forward_history.append(current_directory)
        previous_directory = back_history.pop()
        update_directory_list(previous_directory, dir_listbox, dir_label, pipeline, add_to_history=False)
    else:
        messagebox.showinfo("Info", "Keine vorherigen Verzeichnisse in der Historie.")

def navigate_forward(dir_listbox, dir_label, pipeline):
    global forward_history, current_directory, back_history
    if forward_history:
        back_history.append(current_directory)
        next_directory = forward_history.pop()
        update_directory_list(next_directory, dir_listbox, dir_label, pipeline, add_to_history=False)
    else:
        messagebox.showinfo("Info", "Keine weiteren Verzeichnisse in der Historie.")

def remove_pipeline_step(event, pipeline_tree, pipeline):
    if selected_item := pipeline_tree.selection():
        try:
            step_index = int(selected_item[0]) - 1
            if 0 <= step_index < len(pipeline.steps):
                del pipeline.steps[step_index]
                pipeline.display_status()
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Schritt-ID.")

def show_pipeline_menu(event, pipeline_tree, pipeline_menu):
    if selected_item := pipeline_tree.identify_row(event.y):
        pipeline_tree.selection_set(selected_item)
        pipeline_menu.post(event.x_root, event.y_root)

def build_analyze_gui():
    root = tk.Tk()
    root.title("Analyse- und Empfehlungssystem")
    root.geometry("825x800")
    root.resizable(False, False)

    style = ttk.Style(root)
    available_themes = style.theme_names()
    if "vista" in available_themes:
        style.theme_use("vista")
    else:
        style.theme_use("default")

    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(2, weight=1)

    # Label für das aktuelle Verzeichnis
    dir_label = ttk.Label(
        main_frame,
        text=f"Aktuelles Verzeichnis: {current_directory}",
        anchor="w",
        font=("Helvetica", 12, "bold"),
    )
    dir_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

    # Frame für die Dateiliste
    frame = ttk.Frame(main_frame)
    frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.grid(row=0, column=1, sticky="ns")

    dir_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
    dir_listbox.grid(row=0, column=0, sticky="nsew")
    scrollbar.config(command=dir_listbox.yview)

    # Navigations-Frame
    nav_frame = ttk.Frame(main_frame)
    nav_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 5))

    # Aktionen-Frame
    actions_frame = ttk.LabelFrame(
        main_frame, text="Skripte auswählen", padding=(10, 10)
    )
    actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
    actions_frame.columnconfigure(0, weight=1)

    # Checkbuttons für die Analyse
    action_vars = {}
    for action_name in analysis_actions.keys():
        var = tk.BooleanVar()
        cb = ttk.Checkbutton(actions_frame, text=action_name, variable=var)
        cb.pack(side="left", padx=5, pady=5)
        action_vars[action_name] = var

    # Pipeline-Frame
    pipeline_frame = ttk.LabelFrame(
        main_frame, text="Pipeline Schritte", padding=(10, 10)
    )
    pipeline_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
    pipeline_frame.columnconfigure(0, weight=1)

    pipeline_tree = ttk.Treeview(
        pipeline_frame,
        columns=("Status", "Name", "Datei", "Duration"),
        show="headings",
        selectmode="browse",
    )
    pipeline_tree.heading("Status", text="Status")
    pipeline_tree.heading("Name", text="Aktion")
    pipeline_tree.heading("Datei", text="Datei")
    pipeline_tree.heading("Duration", text="Duration")
    pipeline_tree.column("Status", width=100, anchor="center")
    pipeline_tree.column("Name", width=200, anchor="w")
    pipeline_tree.column("Datei", width=350, anchor="w")
    pipeline_tree.column("Duration", width=80, anchor="center")
    pipeline_tree.pack(fill="both", expand=True)

    pipeline_scrollbar = ttk.Scrollbar(
        pipeline_frame, orient="vertical", command=pipeline_tree.yview
    )
    pipeline_tree.configure(yscrollcommand=pipeline_scrollbar.set)
    pipeline_scrollbar.pack(side="right", fill="y")

    pipeline_menu = tk.Menu(root, tearoff=0)
    pipeline = AnalysisPipeline(pipeline_tree)
    pipeline_menu.add_command(
        label="Schritt entfernen",
        command=lambda: remove_pipeline_step(None, pipeline_tree, pipeline),
    )

    def show_pipeline_menu_handler(event):
        show_pipeline_menu(event, pipeline_tree, pipeline_menu)

    pipeline_tree.bind("<Button-3>", show_pipeline_menu_handler)

    # Handler für Doppelklick auf Eintrag in der Dateiliste
    def on_item_double_click(event):
        selection = dir_listbox.curselection()
        if not selection:
            return
        selected_item = dir_listbox.get(selection)
        selected_path = os.path.join(current_directory, selected_item)

        if os.path.isdir(selected_path.rstrip("/")):
            update_directory_list(selected_path.rstrip("/"), dir_listbox, dir_label, pipeline)
        elif selected_item.endswith(".py"):
            global selected_file
            selected_file = selected_path
            confirm_actions()

    # Fügt die ausgewählten Skripte der Pipeline hinzu
    def confirm_actions():
        chosen_scripts = [name for name, var in action_vars.items() if var.get()]
        if not chosen_scripts:
            messagebox.showwarning("Warnung", "Bitte wählen Sie mindestens ein Skript aus.")
            return

        if not selected_file:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine .py Datei aus.")
            return

        for script_name in chosen_scripts:
            func = analysis_actions.get(script_name)
            pipeline.add_step(script_name, func, selected_file)

    dir_listbox.bind("<Double-Button-1>", on_item_double_click)

    # Navigations-Buttons
    def navigate_up_button():
        navigate_up(dir_listbox, dir_label, pipeline)

    def navigate_back_button():
        navigate_back(dir_listbox, dir_label, pipeline)

    def navigate_forward_button():
        navigate_forward(dir_listbox, dir_label, pipeline)

    navigate_up_btn = ttk.Button(
        nav_frame, text="⬆️ Nach oben navigieren", command=navigate_up_button
    )
    navigate_up_btn.pack(side="left")

    navigate_back_btn = ttk.Button(
        nav_frame, text="🔙 Zurück", command=navigate_back_button
    )
    navigate_back_btn.pack(side="left", padx=(10, 0))

    navigate_forward_btn = ttk.Button(
        nav_frame, text="🔜 Vorwärts", command=navigate_forward_button
    )
    navigate_forward_btn.pack(side="left", padx=(5, 0))

    # Maus-Events zum Blättern
    def on_mouse_button(event):
        if event.num == 4:  # "Back"
            navigate_back(dir_listbox, dir_label, pipeline)
        elif event.num == 5:  # "Forward"
            navigate_forward(dir_listbox, dir_label, pipeline)

    root.bind_all("<Button-4>", on_mouse_button)
    root.bind_all("<Button-5>", on_mouse_button)

    # Button zum Ausführen des nächsten Pipelineschritts
    def run_next_step_button():
        pipeline.run_next_step()

    start_button = ttk.Button(main_frame, text="Weiter", command=run_next_step_button)
    start_button.grid(row=5, column=0, sticky="e", padx=10, pady=10)

    # Initiales Laden des aktuellen Verzeichnisses
    update_directory_list(current_directory, dir_listbox, dir_label, pipeline)

    return root

# Starte die GUI
if __name__ == "__main__":
    app = build_analyze_gui()
    app.mainloop()
