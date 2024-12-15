import os
import tkinter as tk
from tkinter import Listbox, Scrollbar, END, ttk, filedialog
from tkinter.messagebox import showinfo, showerror
from refactor import process_refactoring

import ast
import astor
import re
import time
import datetime

# Historienstacks für Navigation
back_history = []
forward_history = []

class PipelineStep:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.outcome = None  # "success" oder "failure"

    def run(self, function, *args, **kwargs):
        """Führt den Schritt aus und protokolliert die Zeit und das Ergebnis."""
        self.start_time = datetime.datetime.now()
        try:
            function(*args, **kwargs)  # Die tatsächliche Funktion des Schrittes
            self.outcome = "success"
        except Exception as e:
            self.outcome = f"failure: {e}"
        finally:
            self.end_time = datetime.datetime.now()

    def get_time_taken(self):
        """Gibt die benötigte Zeit als String zurück."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return f"{str(delta.seconds)} Sekunden"
        return "Not completed"

    def get_status(self):
        """Gibt den aktuellen Status zurück."""
        return {
            "Step": self.name,
            "Outcome": self.outcome or "Running",
            "Time Taken": self.get_time_taken(),
            "Timestamp": self.start_time.strftime("%H:%M:%S") if self.start_time else "N/A",
        }

class Pipeline:
    def __init__(self, status_label):
        self.steps = []
        self.status_label = status_label

    def add_step(self, name, function, *args, **kwargs):
        """Fügt einen Schritt zur Pipeline hinzu und führt ihn aus."""
        step = PipelineStep(name)
        self.steps.append(step)
        step.run(function, *args, **kwargs)
        self.display_status()

    def display_status(self):
        """Aktualisiert die Statusanzeige in der GUI."""
        status_text = "\n".join([
            f"Schritt: {step.get_status()['Step']}\n"
            f"Ergebnis: {step.get_status()['Outcome']}\n"
            f"Zeit: {step.get_status()['Time Taken']}\n"
            f"Startzeit: {step.get_status()['Timestamp']}\n"
            f"{'-'*50}"
            for step in self.steps
        ])
        self.status_label.config(text=status_text)

def list_directory_contents(directory):
    """Listet alle Dateien und Ordner im Verzeichnis auf."""
    contents = []
    for item in os.listdir(directory):
        # Markiere Ordner mit einem Schrägstrich am Ende
        if os.path.isdir(os.path.join(directory, item)):
            contents.append(f"{item}/")
        elif item.endswith(".py"):  # Nur Python-Dateien anzeigen
            contents.append(item)
    return contents

def update_directory_list(directory, add_to_history=True):
    """Aktualisiert die Liste der Dateien und Ordner in der GUI."""
    global current_directory
    if add_to_history:
        back_history.append(current_directory)
        # Beim Navigieren zu einem neuen Verzeichnis wird der Vorwärts-Stack geleert
        forward_history.clear()
    current_directory = directory
    dir_listbox.delete(0, END)
    contents = list_directory_contents(directory)
    for item in contents:
        dir_listbox.insert(END, item)
    dir_label.config(text=f"Aktuelles Verzeichnis: {directory}")
    # Statusanzeige zurücksetzen
    status_label.config(text="")
    if pipeline := getattr(root, 'pipeline', None):
        pipeline.steps = []
        pipeline.display_status()

def extract_functions(file_path):
    """
    Extrahiert alle Funktionen aus einer Python-Datei.
    
    Parameters:
    - file_path (str): Der Pfad zur Python-Datei.
    
    Returns:
    - list of dict: Eine Liste von Dictionaries mit 'name', 'start_line' und 'end_line' für jede Funktion.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    parsed_ast = ast.parse(code)
    functions = []
    
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = node.body[-1].end_lineno if hasattr(node.body[-1], "end_lineno") else node.lineno
            functions.append({
                'name': node.name,
                'start_line': start_line,
                'end_line': end_line
            })
    
    return functions

def show_functions_selection(file_path):
    """
    Öffnet ein neues Fenster mit einer Liste von Funktionen und Kontrollkästchen zur Auswahl.
    
    Parameters:
    - file_path (str): Der Pfad zur Python-Datei.
    """
    functions = extract_functions(file_path)
    if not functions:
        showinfo("Info", "Keine Funktionen in der ausgewählten Datei gefunden.")
        return
    
    # Neues Fenster erstellen
    selection_window = tk.Toplevel(root)
    selection_window.title("Funktionen auswählen zur Refaktorisierung")
    selection_window.geometry("600x400")
    selection_window.resizable(False, False)
    
    # Scrollbar hinzufügen
    canvas = tk.Canvas(selection_window, borderwidth=0)
    scrollbar = ttk.Scrollbar(selection_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Variablen für Kontrollkästchen
    var_dict = {}
    
    for func in functions:
        var = tk.BooleanVar()
        cb = ttk.Checkbutton(scrollable_frame, text=f"{func['name']} (Zeilen {func['start_line']}-{func['end_line']})", variable=var)
        cb.pack(anchor='w', pady=2, padx=10)
        var_dict[func['name']] = {
            'variable': var,
            'start_line': func['start_line'],
            'end_line': func['end_line']
        }
    
    def confirm_selection():
        selected_functions = []
        selected_line_numbers = []
        for func in var_dict.values():
            if func['variable'].get():
                selected_functions.append(func)
                selected_line_numbers.extend(range(func['start_line'], func['end_line'] + 1))
        
        if not selected_functions:
            showinfo("Info", "Keine Funktionen ausgewählt.")
            return
        
        selected_actions = []
        for action, var in action_vars.items():
            if var.get():
                selected_actions.append(action)
        
        if not selected_actions:
            showinfo("Info", "Keine Aktionen ausgewählt.")
            return
        
        pipeline = root.pipeline
        for action in selected_actions:
            step_name = action
            function = action_functions.get(action)
            if function:
                pipeline.add_step(step_name, function, file_path)
        
        # Startet den Refaktorisierungsprozess
        pipeline.add_step("Refaktorisierung", process_refactoring, file_path, list(set(selected_line_numbers)))
        selection_window.destroy()
    
    # Bestätigungsbutton
    confirm_button = ttk.Button(selection_window, text="Refaktorisieren", command=confirm_selection)
    confirm_button.pack(pady=10)

def on_item_double_click(event):
    """Verarbeitung der Doppelklick-Auswahl eines Eintrags in der Liste."""
    selection = dir_listbox.curselection()
    if not selection:
        return  # Keine Auswahl getroffen
    selected_item = dir_listbox.get(selection)
    selected_path = os.path.join(current_directory, selected_item)

    if os.path.isdir(selected_path):  # Wenn ein Ordner ausgewählt wurde
        update_directory_list(selected_path)
    elif selected_item.endswith(".py"):  # Wenn eine Datei ausgewählt wurde
        status_label.config(text=f"Ausgewählte Datei: {selected_path}")
        show_functions_selection(selected_path)

def navigate_up():
    """Navigiert einen Ordner nach oben."""
    parent_directory = os.path.dirname(current_directory)
    update_directory_list(parent_directory)

def navigate_back():
    """Navigiert zum vorherigen Verzeichnis in der Historie."""
    if not back_history:
        status_label.config(text="Keine vorherigen Verzeichnisse in der Historie.")
        return
    forward_history.append(current_directory)
    previous_directory = back_history.pop()
    update_directory_list(previous_directory, add_to_history=False)

def navigate_forward():
    """Navigiert zum nächsten Verzeichnis in der Historie."""
    if not forward_history:
        status_label.config(text="Keine nächsten Verzeichnisse in der Historie.")
        return
    back_history.append(current_directory)
    next_directory = forward_history.pop()
    update_directory_list(next_directory, add_to_history=False)

def on_mouse_button(event):
    """Verarbeitet die Seitentasten der Maus."""
    if event.num == 4:  # "Zurück"-Taste
        navigate_back()
    elif event.num == 5:  # "Vorwärts"-Taste
        navigate_forward()

# GUI erstellen
root = tk.Tk()
root.title("Python Refactoring Tool")
root.geometry("900x700")
root.resizable(False, False)

# Style konfigurieren
style = ttk.Style(root)
style.theme_use('clam')

# Startverzeichnis
current_directory = os.getcwd()

# Verzeichnis-Anzeige
dir_label = ttk.Label(root, text=f"Aktuelles Verzeichnis: {current_directory}", anchor="w", font=("Helvetica", 12, "bold"))
dir_label.pack(fill="x", padx=10, pady=(10, 5))

# Datei- und Ordnerliste
frame = ttk.Frame(root)
frame.pack(padx=10, pady=5, fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

dir_listbox = tk.Listbox(frame, height=20, width=100, yscrollcommand=scrollbar.set, font=("Courier", 10))
dir_listbox.pack(side="left", fill="both", expand=True)
# Bindet den Doppelklick-Event an die neue Handler-Funktion
dir_listbox.bind("<Double-Button-1>", on_item_double_click)

# Bindet die Seitentasten der Maus an die Handler-Funktion
root.bind_all("<Button-4>", on_mouse_button)  # "Zurück" Taste
root.bind_all("<Button-5>", on_mouse_button)  # "Vorwärts" Taste

scrollbar.config(command=dir_listbox.yview)

# Navigationsbuttons
nav_frame = ttk.Frame(root)
nav_frame.pack(fill="x", padx=10, pady=(5, 5))

navigate_up_button = ttk.Button(nav_frame, text="⬆️ Nach oben navigieren", command=navigate_up)
navigate_up_button.pack(side="left")

# Zusätzliche Schaltflächen für Zurück und Vorwärts in der GUI
navigate_back_button = ttk.Button(nav_frame, text="🔙 Zurück", command=navigate_back)
navigate_back_button.pack(side="left", padx=(10, 0))

navigate_forward_button = ttk.Button(nav_frame, text="🔜 Vorwärts", command=navigate_forward)
navigate_forward_button.pack(side="left", padx=(5, 0))

# Auswahlmöglichkeiten
actions_frame = ttk.LabelFrame(root, text="Aktionen auswählen", padding=(10, 10))
actions_frame.pack(fill="x", padx=10, pady=5)

actions = [
    "Pylint",
    "Black",
    "Isort",
    "Move Imports",
    "Refactor",
    "Multi Chain Comparison",
    "Add/Improve Docstrings",
    "Sourcery",
    "SonarQube",
    "Custom Prompt"
]

action_vars = {}
for action in actions:
    var = tk.BooleanVar()
    cb = ttk.Checkbutton(actions_frame, text=action, variable=var)
    cb.pack(side="left", padx=5, pady=5)
    action_vars[action] = var

# Aktionen Funktionen (Platzhalter)
def run_pylint(file_path):
    # Implementiere Pylint-Ausführung
    time.sleep(1)

def run_sonarqube(file_path):
    # Implementiere SonarQube-Ausführung
    time.sleep(1)

def run_black(file_path):
    # Implementiere Black-Ausführung
    time.sleep(1)

def run_isort(file_path):
    # Implementiere Isort-Ausführung
    time.sleep(1)

def move_imports(file_path):
    # Implementiere Move Imports-Ausführung
    time.sleep(1)

def run_refactor(file_path):
    # Implementiere Refactor-Ausführung
    time.sleep(1)

def multi_chain_comparison(file_path):
    # Implementiere Multi Chain Comparison-Ausführung
    time.sleep(1)

def add_improve_docstrings(file_path):
    # Implementiere Add/Improve Docstrings-Ausführung
    time.sleep(1)

def run_sourcery(file_path):
    # Implementiere Sourcery-Ausführung
    time.sleep(1)

def custom_prompt(file_path):
    # Implementiere Custom Prompt-Ausführung
    time.sleep(1)

action_functions = {
    "Pylint": run_pylint,
    "SonarQube": run_sonarqube,
    "Black": run_black,
    "Isort": run_isort,
    "Move Imports": move_imports,
    "Refactor": run_refactor,
    "Multi Chain Comparison": multi_chain_comparison,
    "Add/Improve Docstrings": add_improve_docstrings,
    "Sourcery": run_sourcery,
    "Custom Prompt": custom_prompt
}

# Statusanzeige (neues Label am unteren Ende der GUI)
status_label = ttk.Label(root, text="", anchor="w", foreground="blue", font=("Helvetica", 10))
status_label.pack(fill="x", padx=10, pady=(5, 10))

# Pipeline initialisieren
pipeline = Pipeline(status_label)
root.pipeline = pipeline

# Verzeichnis initial laden ohne zur Historie hinzuzufügen
update_directory_list(current_directory, add_to_history=False)

# Hauptschleife starten
root.mainloop()
