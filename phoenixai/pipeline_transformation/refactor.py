import ast
import astor
import tkinter as tk
import tempfile
import os
import sys
import threading
from tkinter import simpledialog

from phoenixai.utils.base_prompt_handling import (
    save_code_to_file,
    trim_code,
    call_llm,
    read_file,
)


def extract_functions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    parsed_ast = ast.parse(code)
    functions = []
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = (node.body[-1].end_lineno if hasattr(node.body[-1], "end_lineno") else node.lineno)
            functions.append({
                "name": node.name,
                "start_line": start_line,
                "end_line": end_line
            })
    return functions


def extract_function_by_name(file_path, function_name):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    parsed_ast = ast.parse(code)
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            start_line = node.lineno
            end_line = (node.body[-1].end_lineno if hasattr(node.body[-1], "end_lineno") else node.lineno)
            return astor.to_source(node).strip(), start_line, end_line
    raise ValueError(f"Funktion {function_name} nicht gefunden.")


def generate_refactoring_prompt(function_code, function_name):
    return f"""
            Hier ist der Python-Code für die Funktion {function_name}, die refaktoriert werden soll:

            {function_code}

            ### Aufgabe:
            Refaktoriere den Code so, dass jede neue Funktion jeweils nur eine klar abgegrenzte Aufgabe erfüllt.
            Erstelle dafür so viele neue Hilfsfunktionen, wie sinnvoll notwendig – mit aussagekräftigen Namen.
            Die ursprüngliche Funktion {function_name} soll erhalten bleiben, aber zu einer reinen Wrapper-Funktion werden,
            die nur noch die neu erstellten Hilfsfunktionen aufruft und nichts weiter tut.

            Achte darauf:
            1. Überflüssige Wiederholungen oder zu komplizierte Abläufe sollen reduziert werden.
            2. Die neuen Funktionen sollten möglichst selbsterklärende Namen tragen und den Code in logische Einheiten aufteilen.
            3. Die Semantik der Funktion (das letztliche Ergebnis und Verhalten) muss erhalten bleiben.
            4. Gib **nur** den komplett refaktorierten Code zurück, ohne zusätzliche Erklärungen oder Kommentare.
    """



def replace_function_in_code(lines, start_line, end_line, refactored_function):
    return lines[: start_line - 1] + [refactored_function] + lines[end_line:]


def save_selected_functions(selected_functions):
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.tmp')
    for func in selected_functions:
        temp_file.write(func + "\n")
    temp_file.close()
    return temp_file.name


class FunctionSelectionDialog(simpledialog.Dialog):
    def __init__(self, parent, functions, title="Funktionen auswählen zum Refactor"):
        self.functions = functions
        self.vars = {}
        super().__init__(parent, title=title)

    def body(self, master):
        for i, func in enumerate(self.functions):
            var = tk.BooleanVar(master)
            self.vars[func['name']] = var
            label = f"{func['name']} (Zeilen {func['start_line']} - {func['end_line']})"
            tk.Checkbutton(master, text=label, variable=var).grid(row=i, column=0, sticky="w", padx=10, pady=2)
        return None  # kein initialer Fokus

    def apply(self):
        self.result = [name for name, var in self.vars.items() if var.get()]


def select_functions_to_refactor(file_path):
    functions = extract_functions(file_path)
    root = tk.Tk()
    root.withdraw()  # Hauptfenster unsichtbar
    dialog = FunctionSelectionDialog(root, functions)
    selected = dialog.result if dialog.result is not None else []
    root.destroy()
    return selected


def process_single_function(file_path, func_name):
    try:
        function_code, start_line, end_line = extract_function_by_name(file_path, func_name)
    except ValueError as e:
        print(f"[Refactor] {e}", flush=True)
        return
    prompt = generate_refactoring_prompt(function_code, func_name)

    # Asynchroner Aufruf von call_llm in einem separaten Thread
    result_container = {}
    def llm_call():
        result_container['result'] = call_llm(prompt)
    thread = threading.Thread(target=llm_call)
    thread.start()
    thread.join(timeout=60)  # Warte maximal 60 Sekunden
    if thread.is_alive():
        return
    refactored_code = result_container.get('result', '')
    trimmed_refactored_code = trim_code(refactored_code)
    try:
        ast.parse(trimmed_refactored_code)
    except SyntaxError as e:
        print(f"[Refactor] Syntaxfehler im LLM-Code für {func_name}: {e}", flush=True)
        return
    original_code = read_file(file_path)
    lines = original_code.splitlines()
    try:
        _, current_start, current_end = extract_function_by_name(file_path, func_name)
    except ValueError as e:
        print(f"[Refactor] Funktion {func_name} nicht mehr gefunden: {e}", flush=True)
        return
    updated_lines = replace_function_in_code(lines, current_start, current_end, trimmed_refactored_code)
    new_code = "\n".join(updated_lines)
    save_code_to_file(file_path, new_code)
