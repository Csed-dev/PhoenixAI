import ast
import os
import re

import astor
import google.generativeai as genai
from base_prompt_handling import save_code_to_file, trim_code
from dotenv import load_dotenv

# LLM-Konfiguration
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY nicht gesetzt. Bitte setzen Sie die Umgebungsvariable."
    )

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_functions_by_lines(file_path, line_numbers):
    """Extrahiert Funktionen basierend auf Zeilennummern."""
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    parsed_ast = ast.parse(code)
    functions = []

    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = (
                node.body[-1].end_lineno
                if hasattr(node.body[-1], "end_lineno")
                else start_line
            )
            if any(start_line <= line <= end_line for line in line_numbers):
                functions.append(astor.to_source(node).strip())

    if not functions:
        raise ValueError("Keine Funktionen in den angegebenen Zeilen gefunden.")
    return functions


def generate_refactoring_prompt(functions):
    """Generiert den Prompt für das LLM."""
    function_code = "\n\n".join(functions)
    return f"""
            Hier ist der Python-Code für die Funktionen, die refaktoriert werden sollen.:

            {function_code}

            ### Aufgabe:
            Refaktoriere jede Funktion so, dass sie möglichst nur einen Zweck erfüllt.
            Überprüfe den Code auf Wiederholungen und unnötige Komplexität. 
            Falls nötig, teile größere Funktionen in kleinere, klar benannte Unterfunktionen auf. 
            Stelle sicher, dass alle Teile des ursprünglichen Codes erhalten bleiben.
            Ziel ist es, die Struktur zu verbessern, um die einzelnen Funktionen besser verstehen zu 
            können und um die Wartbarkeit zu erhöhen 
            Antworte nur mit dem refaktorierten Code.

            Hinweise:
            1. Jede Funktion oder Klasse sollte klar definierte Aufgaben haben.
            2. Überflüssige Wiederholungen im Code sollten vermieden werden.
            3. Verändere nicht die eigentliche Semantik des Codes. Die Funktionen sollen genau das selbe Ergebnis liefern.

            Gib **nur** den modularisierten Code zurück, ohne zusätzliche Erklärungen oder Kommentare außerhalb des Codes.
    """


def call_llm_for_refactoring(prompt):
    """Ruft das LLM auf, um Code zu refaktorisieren."""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.7),
        )
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            raise ValueError("Keine Antwort vom LLM erhalten.")
    except Exception as e:
        raise RuntimeError(f"Fehler beim LLM-Aufruf: {e}")


def read_original_code(file_path):
    """
    Liest den Originalcode aus der angegebenen Datei.

    Parameters:
    - file_path (str): Der Pfad zur Originaldatei.

    Returns:
    - str: Der Inhalt der Originaldatei.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError as e:
        raise IOError(f"Fehler beim Lesen der Datei '{file_path}': {e}")


def parse_ast(original_code):
    """
    Parst den Originalcode und gibt den AST zurück.

    Parameters:
    - original_code (str): Der Inhalt des Originalcodes.

    Returns:
    - ast.AST: Der geparste Abstract Syntax Tree (AST) des Codes.
    """
    try:
        return ast.parse(original_code)
    except SyntaxError as e:
        raise SyntaxError(f"Syntaxfehler beim Parsen der Datei: {e}")


def identify_functions_to_remove(parsed_ast, line_numbers):
    """
    Identifiziert die Funktionen, die basierend auf den angegebenen Zeilennummern entfernt werden sollen.

    Parameters:
    - parsed_ast (ast.AST): Der geparste AST des Originalcodes.
    - line_numbers (list of int): Die Zeilennummern der Funktionen, die refaktoriert wurden.

    Returns:
    - set of int: Die Indizes der Zeilen, die entfernt werden sollen.
    """
    lines_to_delete = set()
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1  # 0-basierter Index
            end_line = (
                node.body[-1].end_lineno - 1
                if hasattr(node.body[-1], "end_lineno")
                else start_line
            )
            # Prüfe, ob die Funktion in den angegebenen Zeilennummern liegt
            if any(start_line <= (line - 1) <= end_line for line in line_numbers):
                lines_to_delete.update(range(start_line, end_line + 1))
    return lines_to_delete


def remove_functions_from_code(lines, lines_to_delete):
    """
    Entfernt die angegebenen Zeilen aus dem Code.

    Parameters:
    - lines (list of str): Die Zeilen des Originalcodes.
    - lines_to_delete (set of int): Die Indizes der Zeilen, die entfernt werden sollen.

    Returns:
    - list of str: Die verbleibenden Zeilen nach dem Entfernen.
    """
    return [line for idx, line in enumerate(lines) if idx not in lines_to_delete]


def add_refactored_functions(lines, refactored_functions, functions_sorted):
    """
    Fügt die refaktorierten Funktionen zum Code hinzu.

    Parameters:
    - lines (list of str): Die verbleibenden Zeilen des Codes.
    - refactored_functions (list of str): Eine Liste der refaktorierten Funktionsdefinitionen als Strings.
    - functions_sorted (list of dict): Die Liste der Funktionen, sortiert nach start_line absteigend.

    Returns:
    - list of str: Die aktualisierten Zeilen des Codes.
    """
    for func, refactored in zip(functions_sorted, refactored_functions):
        start = func['start_line'] - 1
        end = func['end_line']
        refactored_lines = refactored.splitlines()
        lines[start:end] = refactored_lines
    return lines


def save_refactored_code(file_path, refactored_functions, line_numbers):
    """Speichert den refaktorierten Code direkt in der Originaldatei."""
    original_code = read_original_code(file_path)
    parsed_ast = parse_ast(original_code)
    lines = original_code.splitlines()
    functions = extract_functions_by_lines(file_path, line_numbers)
    functions_sorted = sorted(functions, key=lambda x: x['start_line'], reverse=True)
    refactored_functions_sorted = sorted(refactored_functions, key=lambda x: functions[refactored_functions.index(x)]['start_line'], reverse=True)
    updated_lines = add_refactored_functions(lines, refactored_functions, functions_sorted)
    
    refactored_code = "\n".join(updated_lines)
    
    # Speichere den refaktorierten Code direkt in der Originaldatei
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(refactored_code)
    except IOError as e:
        raise IOError(f"Fehler beim Schreiben der Datei '{file_path}': {e}")
    
    print(f"Die Datei wurde erfolgreich refaktoriert und überschrieben: {file_path}")
    return file_path


def process_refactoring(file_path, line_numbers):
    """Kompletter Prozess zur Refaktorisierung von Funktionen."""
    try:
        functions = extract_functions_by_lines(file_path, line_numbers)
        prompt = generate_refactoring_prompt(functions)
        refactored_code = call_llm_for_refactoring(prompt)
        trimmed_refactored_code = trim_code(refactored_code)

        # Extrahiere die refaktorierten Funktionen
        refactored_functions = [
            f.strip() for f in re.split(r"\n\s*\n", trimmed_refactored_code) if f.strip()
        ]
        saved_file_path = save_refactored_code(file_path, refactored_functions, line_numbers)
        return saved_file_path
    except Exception as e:
        raise RuntimeError(f"Fehler während der Refaktorisierung: {e}")
