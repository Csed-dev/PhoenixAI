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
    print("[DEBUG] extract_functions gestartet", flush=True)
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
    print("[DEBUG] extract_functions beendet, gefunden:", functions, flush=True)
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
            Refaktoriere die Funktion so, dass sie möglichst nur einen Zweck erfüllt.
            Überprüfe den Code auf Wiederholungen und unnötige Komplexität.
            Erstelle **zwei** Funktionsdefinitionen:
            1. Eine neue Funktion, benannt als "{function_name}_refactored", die den refaktorierten Code enthält.
            2. Die ursprüngliche Funktion {function_name} soll erhalten bleiben, jedoch mit einem modifizierten Funktionskörper,
               der **nur** einen Aufruf der neuen Funktion ({function_name}_refactored) beinhaltet.
            So bleibt der ursprüngliche Funktionskopf erhalten.
            Gib **nur** den modularisierten Code zurück, ohne zusätzliche Erklärungen oder Kommentare.
    """


def replace_function_in_code(lines, start_line, end_line, refactored_function):
    return lines[: start_line - 1] + [refactored_function] + lines[end_line:]


def save_selected_functions(selected_functions):
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.tmp')
    for func in selected_functions:
        temp_file.write(func + "\n")
    temp_file.close()
    print(f"[DEBUG] Temporäre Datei mit ausgewählten Funktionen erstellt: {temp_file.name}", flush=True)
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
    print("[DEBUG] select_functions_to_refactor gestartet", flush=True)
    functions = extract_functions(file_path)
    root = tk.Tk()
    root.withdraw()  # Hauptfenster unsichtbar
    dialog = FunctionSelectionDialog(root, functions)
    selected = dialog.result if dialog.result is not None else []
    print("[DEBUG] Dialog beendet, ausgewählte Funktionen:", selected, flush=True)
    root.destroy()
    return selected


def process_single_function(file_path, func_name):
    print(f"[DEBUG] process_single_function gestartet für: {func_name}", flush=True)
    try:
        function_code, start_line, end_line = extract_function_by_name(file_path, func_name)
        print(f"[DEBUG] Funktion {func_name} extrahiert (Zeilen {start_line}-{end_line}).", flush=True)
    except ValueError as e:
        print(f"[Refactor] {e}", flush=True)
        return
    prompt = generate_refactoring_prompt(function_code, func_name)
    print(f"[DEBUG] Sende Prompt an LLM für {func_name} ...", flush=True)

    # Asynchroner Aufruf von call_llm in einem separaten Thread
    result_container = {}
    def llm_call():
        result_container['result'] = call_llm(prompt)
    thread = threading.Thread(target=llm_call)
    thread.start()
    thread.join(timeout=60)  # Warte maximal 60 Sekunden
    if thread.is_alive():
        print(f"[DEBUG] LLM-Aufruf für {func_name} timed out.", flush=True)
        return
    refactored_code = result_container.get('result', '')
    print(f"[DEBUG] LLM hat geantwortet für {func_name}: {refactored_code}", flush=True)
    trimmed_refactored_code = trim_code(refactored_code)
    try:
        ast.parse(trimmed_refactored_code)
        print(f"[DEBUG] Refaktorierter Code für {func_name} erfolgreich geparst.", flush=True)
    except SyntaxError as e:
        print(f"[Refactor] Syntaxfehler im LLM-Code für {func_name}: {e}", flush=True)
        return
    original_code = read_file(file_path)
    lines = original_code.splitlines()
    try:
        _, current_start, current_end = extract_function_by_name(file_path, func_name)
        print(f"[DEBUG] Aktuelle Position der Funktion {func_name} ermittelt: Zeilen {current_start}-{current_end}", flush=True)
    except ValueError as e:
        print(f"[Refactor] Funktion {func_name} nicht mehr gefunden: {e}", flush=True)
        return
    updated_lines = replace_function_in_code(lines, current_start, current_end, trimmed_refactored_code)
    new_code = "\n".join(updated_lines)
    save_code_to_file(file_path, new_code)
    print(f"[DEBUG] Funktion {func_name} wurde refactored und ersetzt.", flush=True)
