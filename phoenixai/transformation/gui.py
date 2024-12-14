import os
import tkinter as tk
from tkinter import Listbox, Scrollbar, END, ttk
from tkinter.messagebox import showinfo, showerror
from refactor import process_refactoring, extract_functions_by_lines

import ast
import astor
import re
import git  # Importiere GitPython

# Historienstacks für Navigation
back_history = []
forward_history = []

selected_file_path = None  # Globale Variable zur Speicherung des ausgewählten Dateipfads

def list_directory_contents(directory):
    """Listet alle Dateien und Ordner im Verzeichnis auf."""
    contents = []
    for item in os.listdir(directory):
        # Markiere Ordner mit einem Schrägstrich am Ende
        if os.path.isdir(os.path.join(directory, item)):
            contents.append(item + "/")
        else:
            if item.endswith(".py"):  # Nur Python-Dateien anzeigen
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
    git_status_label.config(text="")  # Git-Status zurücksetzen

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
    global selected_file_path
    selected_file_path = file_path  # Setze den ausgewählten Pfad
    
    functions = extract_functions(file_path)
    if not functions:
        showinfo("Info", "Keine Funktionen in der ausgewählten Datei gefunden.")
        return
    
    # Neues Fenster erstellen
    selection_window = tk.Toplevel(root)
    selection_window.title("Funktionen auswählen zur Refaktorisierung")
    selection_window.geometry("600x400")
    
    # Scrollbar hinzufügen
    canvas = tk.Canvas(selection_window)
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
        
        # Startet den Refaktorisierungsprozess
        process_refactoring(file_path, list(set(selected_line_numbers)))
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

def get_git_repo(directory):
    """
    Gibt das Git-Repository für das angegebene Verzeichnis zurück.
    Wenn kein Repository gefunden wird, gibt es None zurück.
    
    Parameters:
    - directory (str): Das Verzeichnis, in dem nach einem Git-Repository gesucht wird.
    
    Returns:
    - git.Repo oder None: Das Git-Repository-Objekt oder None, wenn kein Repository gefunden wurde.
    """
    try:
        repo = git.Repo(directory, search_parent_directories=True)
        return repo
    except git.exc.InvalidGitRepositoryError:
        return None

def show_git_status(file_path):
    """
    Zeigt den Git-Status der Datei an.
    
    Parameters:
    - file_path (str): Der Pfad zur Datei.
    """
    repo = get_git_repo(current_directory)
    if repo is None:
        git_status_label.config(text="Kein Git-Repository gefunden.")
        return
    
    # Relativer Pfad zur Datei im Repository
    try:
        rel_path = os.path.relpath(file_path, repo.working_tree_dir)
    except ValueError:
        git_status_label.config(text="Die Datei gehört nicht zum Git-Repository.")
        return
    
    # Git-Status abrufen
    if rel_path in repo.untracked_files:
        status = "untracked"
    elif any(rel_path == item.a_path for item in repo.index.diff(None)):
        status = "modified"
    else:
        status = "clean"
    
    git_status_label.config(text=f"Git-Status der Datei: {status}")

def stage_changes():
    """
    Staget die Änderungen der Datei im Git-Repository.
    Verwendet die globale Variable selected_file_path.
    """
    global selected_file_path
    if selected_file_path is None:
        showerror("Fehler", "Keine Datei ausgewählt.")
        return
    
    repo = get_git_repo(current_directory)
    if repo is None:
        showerror("Fehler", "Kein Git-Repository gefunden.")
        return
    
    try:
        rel_path = os.path.relpath(selected_file_path, repo.working_tree_dir)
        repo.index.add([rel_path])
        showinfo("Erfolg", f"Änderungen an '{rel_path}' wurden gestaged.")
        show_git_status(selected_file_path)
    except Exception as e:
        showerror("Fehler", f"Fehler beim Stagen der Änderungen: {e}")

def revert_changes():
    """
    Setzt die Änderungen der Datei im Git-Repository zurück.
    Verwendet die globale Variable selected_file_path.
    """
    global selected_file_path
    if selected_file_path is None:
        showerror("Fehler", "Keine Datei ausgewählt.")
        return
    
    repo = get_git_repo(current_directory)
    if repo is None:
        showerror("Fehler", "Kein Git-Repository gefunden.")
        return
    
    try:
        rel_path = os.path.relpath(selected_file_path, repo.working_tree_dir)
        repo.git.checkout('--', rel_path)
        showinfo("Erfolg", f"Änderungen an '{rel_path}' wurden zurückgesetzt.")
        show_git_status(selected_file_path)
    except Exception as e:
        showerror("Fehler", f"Fehler beim Zurücksetzen der Änderungen: {e}")

def show_refactor_options(file_path):
    """
    Zeigt Optionen zum Stagen oder Revertieren nach der Refaktorisierung an.
    
    Parameters:
    - file_path (str): Der Pfad zur Datei.
    """
    # Git-Status anzeigen
    show_git_status(file_path)
    
    # Buttons zum Stagen und Revertieren hinzufügen, falls die Datei modifiziert wurde
    repo = get_git_repo(current_directory)
    if repo is None:
        return
    
    rel_path = os.path.relpath(file_path, repo.working_tree_dir)
    if rel_path in repo.untracked_files or any(rel_path == item.a_path for item in repo.index.diff(None)):
        stage_button.pack(pady=5)
        revert_button.pack(pady=5)
    else:
        stage_button.pack_forget()
        revert_button.pack_forget()

def process_refactoring(file_path, line_numbers):
    """Kompletter Prozess zur Refaktorisierung von Funktionen."""
    try:
        backup_original_file(file_path)
        functions = extract_functions_by_lines(file_path, line_numbers)
        prompt = generate_refactoring_prompt(functions)
        refactored_code = call_llm_for_refactoring(prompt)
        trimmed_refactored_code = trim_code(refactored_code)

        # Extrahiere die refaktorierten Funktionen
        refactored_functions = [
            f.strip() for f in re.split(r"\n\s*\n", trimmed_refactored_code) if f.strip()
        ]
        save_refactored_code(file_path, refactored_functions, line_numbers)
        status_label.config(text="Erfolg: Die Datei wurde erfolgreich refaktoriert!")
        
        # Zeige Git-Optionen an
        show_refactor_options(file_path)
    except Exception as e:
        status_label.config(text=f"Fehler: Ein Fehler ist aufgetreten: {e}")

def backup_original_file(file_path):
    """
    Erstellt eine Sicherungskopie der Originaldatei.
    
    Parameters:
    - file_path (str): Der Pfad zur Originaldatei.
    """
    backup_path = file_path + ".bak"
    try:
        with open(file_path, "r", encoding="utf-8") as original, open(backup_path, "w", encoding="utf-8") as backup:
            backup.write(original.read())
        print(f"Sicherungskopie erstellt: {backup_path}")
    except IOError as e:
        raise IOError(f"Fehler beim Erstellen der Sicherungskopie: {e}")

# GUI erstellen
root = tk.Tk()
root.title("Python Refactoring Tool")
root.geometry("800x600")  # Setze eine geeignete Fenstergröße

# Startverzeichnis
current_directory = os.getcwd()

# Verzeichnis-Anzeige
dir_label = tk.Label(root, text=f"Aktuelles Verzeichnis: {current_directory}", anchor="w")
dir_label.pack(fill="x", padx=10, pady=(10, 5))

# Datei- und Ordnerliste
frame = tk.Frame(root)
frame.pack(padx=10, pady=5, fill="both", expand=True)

scrollbar = Scrollbar(frame)
scrollbar.pack(side="right", fill="y")

dir_listbox = Listbox(frame, height=25, width=100, yscrollcommand=scrollbar.set)
dir_listbox.pack(side="left", fill="both", expand=True)
# Bindet den Doppelklick-Event an die neue Handler-Funktion
dir_listbox.bind("<Double-Button-1>", on_item_double_click)

# Bindet die Seitentasten der Maus an die Handler-Funktion
root.bind_all("<Button-4>", on_mouse_button)  # "Zurück" Taste
root.bind_all("<Button-5>", on_mouse_button)  # "Vorwärts" Taste

scrollbar.config(command=dir_listbox.yview)

# Navigationsbuttons
nav_frame = tk.Frame(root)
nav_frame.pack(fill="x", padx=10, pady=(5, 5))

navigate_up_button = tk.Button(nav_frame, text="⬆️ Nach oben navigieren", command=navigate_up)
navigate_up_button.pack(side="left")

# Zusätzliche Schaltflächen für Zurück und Vorwärts in der GUI
navigate_back_button = tk.Button(nav_frame, text="🔙 Zurück", command=navigate_back)
navigate_back_button.pack(side="left", padx=(10, 0))

navigate_forward_button = tk.Button(nav_frame, text="🔜 Vorwärts", command=navigate_forward)
navigate_forward_button.pack(side="left", padx=(5, 0))

# Statusanzeige (neues Label am unteren Ende der GUI)
status_frame = tk.Frame(root)
status_frame.pack(fill="x", padx=10, pady=(5, 10))

status_label = tk.Label(status_frame, text="", anchor="w", fg="blue")
status_label.pack(fill="x", side="top")

git_status_label = tk.Label(status_frame, text="", anchor="w", fg="green")
git_status_label.pack(fill="x", side="top")

# Buttons zum Stagen und Revertieren (initial versteckt)
stage_button = ttk.Button(status_frame, text="Änderungen Stagen", command=stage_changes)
revert_button = ttk.Button(status_frame, text="Änderungen Revertieren", command=revert_changes)
stage_button.pack_forget()
revert_button.pack_forget()

# Verzeichnis initial laden ohne zur Historie hinzuzufügen
update_directory_list(current_directory, add_to_history=False)

# Hauptschleife starten
root.mainloop()
