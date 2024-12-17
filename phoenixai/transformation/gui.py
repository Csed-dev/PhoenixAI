import os
import tkinter as tk
from tkinter import END, ttk
from tkinter.messagebox import showerror, showinfo
from refactor import extract_functions

from pipeline import Pipeline, action_functions

back_history = []
forward_history = []
current_directory = os.getcwd()
selected_file = None


def remove_pipeline_step(event, pipeline_tree, pipeline):
    if selected_item := pipeline_tree.selection():
        # Ermitteln Sie den Index des ausgewählten Elements
        try:
            step_index = int(selected_item[0]) - 1  # Treeview-IDs beginnen bei 1
            if 0 <= step_index < len(pipeline.steps):
                # Schritt aus der Pipeline entfernen
                del pipeline.steps[step_index]
                # Treeview aktualisieren
                pipeline.display_status()
        except ValueError:
            showerror("Fehler", "Ungültige Schritt-ID.")


def show_pipeline_menu(event, pipeline_tree, pipeline_menu):
    if selected_item := pipeline_tree.identify_row(event.y):
        pipeline_tree.selection_set(selected_item)
        pipeline_menu.post(event.x_root, event.y_root)


def list_directory_contents(directory):
    """Listet alle Dateien und Ordner im Verzeichnis auf."""
    contents = []
    for item in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, item)):
            contents.append(f"{item}/")
        elif item.endswith(".py"):
            contents.append(item)
    return contents


def update_directory_list(directory, dir_listbox, dir_label, pipeline):
    """Aktualisiert die Liste der Dateien und Ordner in der GUI."""
    global current_directory
    back_history.append(current_directory)
    forward_history.clear()
    current_directory = directory
    dir_listbox.delete(0, END)
    contents = list_directory_contents(directory)
    for item in contents:
        dir_listbox.insert(END, item)
    dir_label.config(text=f"Aktuelles Verzeichnis: {directory}")
    pipeline.reset()



def navigate_up(dir_listbox, dir_label, pipeline):
    """Navigiert ein Verzeichnis nach oben."""
    global current_directory
    parent_directory = os.path.dirname(current_directory)
    if parent_directory != current_directory:  # Verhindert, dass wir über das Wurzelverzeichnis hinausgehen
        update_directory_list(parent_directory, dir_listbox, dir_label, pipeline)
    else:
        showinfo("Info", "Sie befinden sich bereits im Wurzelverzeichnis.")

def navigate_back(dir_listbox, dir_label, pipeline):
    """Navigiert zum vorherigen Verzeichnis in der Historie."""
    global back_history, current_directory, forward_history
    if back_history:
        forward_history.append(current_directory)
        previous_directory = back_history.pop()
        update_directory_list(previous_directory, dir_listbox, dir_label, pipeline)
    else:
        showinfo("Info", "Keine vorherigen Verzeichnisse in der Historie.")

def navigate_forward(dir_listbox, dir_label, pipeline):
    """Navigiert zum nächsten Verzeichnis in der Historie."""
    global forward_history, current_directory, back_history
    if forward_history:
        back_history.append(current_directory)
        next_directory = forward_history.pop()
        update_directory_list(next_directory, dir_listbox, dir_label, pipeline)
    else:
        showinfo("Info", "Keine weiteren Verzeichnisse in der Historie.")



def build_gui():
    root = tk.Tk()
    root.title("Python Refactoring Tool")
    root.geometry("800x800")
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

    dir_label = ttk.Label(
        main_frame,
        text=f"Aktuelles Verzeichnis: {current_directory}",
        anchor="w",
        font=("Helvetica", 12, "bold"),
    )
    dir_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

    frame = ttk.Frame(main_frame)
    frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.grid(row=0, column=1, sticky="ns")

    dir_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
    dir_listbox.grid(row=0, column=0, sticky="nsew")
    scrollbar.config(command=dir_listbox.yview)

    nav_frame = ttk.Frame(main_frame)
    nav_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 5))

    actions_frame = ttk.LabelFrame(
        main_frame, text="Aktionen auswählen", padding=(10, 10)
    )
    actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
    actions_frame.columnconfigure(0, weight=1)

    actions = [
        "Refactor",
        "Add/Improve Docstrings",
        "Type Annotation Updater",
        "Move Imports",
        "Isort",
        "Black",
        "Pylint",
        "Sourcery",
    ]

    action_vars = {}
    for action in actions:
        var = tk.BooleanVar()
        cb = ttk.Checkbutton(actions_frame, text=action, variable=var)
        cb.pack(side="left", padx=5, pady=5)
        action_vars[action] = var

    pipeline_frame = ttk.LabelFrame(
        main_frame, text="Pipeline Schritte", padding=(10, 10)
    )
    pipeline_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
    pipeline_frame.columnconfigure(0, weight=1)

    # Korrigierte Spaltennamen: Verwende "Duration" konsistent
    pipeline_tree = ttk.Treeview(
        pipeline_frame,
        columns=("Status", "Aktion", "Datei", "Duration"),
        show="headings",
        selectmode="browse",
    )
    pipeline_tree.heading("Status", text="Status")
    pipeline_tree.heading("Aktion", text="Aktion")
    pipeline_tree.heading("Datei", text="Datei")
    pipeline_tree.heading("Duration", text="Duration")
    pipeline_tree.column("Status", width=100, anchor="center")
    pipeline_tree.column("Aktion", width=200, anchor="w")
    pipeline_tree.column("Datei", width=400, anchor="w")
    pipeline_tree.column("Duration", width=100, anchor="center")
    pipeline_tree.pack(fill="both", expand=True)

    pipeline_scrollbar = ttk.Scrollbar(
        pipeline_frame, orient="vertical", command=pipeline_tree.yview
    )
    pipeline_tree.configure(yscrollcommand=pipeline_scrollbar.set)
    pipeline_scrollbar.pack(side="right", fill="y")

    pipeline_menu = tk.Menu(root, tearoff=0)
    pipeline = Pipeline(pipeline_tree)

    pipeline_menu.add_command(
        label="Schritt entfernen",
        command=lambda: remove_pipeline_step(None, pipeline_tree, pipeline),
    )

    def show_pipeline_menu_handler(event):
        show_pipeline_menu(event, pipeline_tree, pipeline_menu)

    pipeline_tree.bind("<Button-3>", show_pipeline_menu_handler)

    def on_item_double_click(event):
        """Verarbeitung der Doppelklick-Auswahl eines Eintrags in der Liste."""
        selection = dir_listbox.curselection()
        if not selection:
            return  # Keine Auswahl getroffen
        selected_item = dir_listbox.get(selection)
        selected_path = os.path.join(current_directory, selected_item)

        if os.path.isdir(selected_path):
            update_directory_list(selected_path, dir_listbox, dir_label, pipeline)
        elif selected_item.endswith(".py"):
            global selected_file
            selected_file = selected_path
            confirm_actions()

    def confirm_actions():
        """Bestätigt die ausgewählten Aktionen und handelt entsprechend."""
        chosen_actions = [name for name, var in action_vars.items() if var.get()]
        if not chosen_actions:
            showinfo("Info", "Keine Aktionen ausgewählt.")
            return

        if "Refactor" in chosen_actions:
            # Entferne "Refactor" aus den allgemeinen Aktionen
            chosen_actions.remove("Refactor")
            # Füge die nicht-Refactor Aktionen hinzu
            for action in chosen_actions:
                function = action_functions.get(action)
                if function:
                    pipeline.add_step(action, function, selected_file)
            # Zeige das Funktionen-Auswahlfenster für Refactor
            show_functions_selection(
                selected_file, root, pipeline, action_vars, pipeline_tree
            )
        else:
            # Füge alle Aktionen direkt hinzu
            for action in chosen_actions:
                function = action_functions.get(action)
                if function:
                    pipeline.add_step(action, function, selected_file)


    def show_functions_selection(file_path, root, pipeline, action_vars, pipeline_tree):
        """
        Öffnet ein neues Fenster mit einer Liste von Funktionen und Kontrollkästchen zur Auswahl.

        Parameters:
        - file_path (str): Der Pfad zur Python-Datei.
        """
        functions = extract_functions(file_path)

        selection_window = tk.Toplevel(root)
        selection_window.title("Funktionen auswählen zur Refaktorisierung")
        selection_window.geometry("600x400")
        selection_window.resizable(False, False)

        canvas = tk.Canvas(selection_window, borderwidth=0)
        scrollbar = ttk.Scrollbar(
            selection_window, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        var_dict = {}

        for func in functions:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(
                scrollable_frame,
                text=f"{func['name']} (Zeilen {func['start_line']}-{func['end_line']})",
                variable=var,
            )
            cb.pack(anchor="w", pady=2, padx=10)
            var_dict[func["name"]] = {
                "variable": var,
                "start_line": func["start_line"],
                "end_line": func["end_line"],
            }

        # In gui.py, in der Funktion confirm_refactor_selection():
        def confirm_refactor_selection():
            selected_functions = [
                name for name, info in var_dict.items() if info["variable"].get()
            ]
            if not selected_functions:
                showinfo("Info", "Keine Funktionen ausgewählt für Refaktorisierung.")
                return

            # line_numbers wird nicht mehr benötigt, da wir die gesamte Datei refaktorisieren
            # pipeline.add_step("Refactor", action_functions["Refactor"], selected_file, line_numbers=line_numbers)
            pipeline.add_step("Refactor", action_functions["Refactor"], selected_file)

            showinfo(
                "Info",
                "Die ausgewählten Refactor-Aktionen wurden der Pipeline hinzugefügt."
            )
            selection_window.destroy()

        confirm_button = ttk.Button(
            selection_window,
            text="Refaktorierung bestätigen",
            command=confirm_refactor_selection,
        )
        confirm_button.pack(pady=10)

    dir_listbox.bind("<Double-Button-1>", lambda event: on_item_double_click(event))

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

    def mouse_button_handler(event):
        on_mouse_button(event, dir_listbox, pipeline)

    def on_mouse_button(event, dir_listbox, pipeline):
        """Verarbeitet die Seitentasten der Maus."""
        if event.num == 4:
            navigate_back(dir_listbox, dir_label, pipeline)
        elif event.num == 5:
            navigate_forward(dir_listbox, dir_label, pipeline)

    def run_next_step(pipeline):
        """Führt den nächsten Schritt der Pipeline aus."""
        pipeline.run_next_step()

    def run_next_step_button():
        run_next_step(pipeline)

    start_button = ttk.Button(main_frame, text="Weiter", command=run_next_step_button)
    start_button.grid(row=5, column=0, sticky="e", padx=10, pady=10)

    # Kontextmenü zum Entfernen von Schritten
    def context_menu_handler(event):
        show_pipeline_menu_handler(event)

    pipeline_tree.bind("<Button-3>", context_menu_handler)

    # Verzeichnis initial laden ohne zur Historie hinzuzufügen
    update_directory_list(current_directory, dir_listbox, dir_label, pipeline)

    return root
