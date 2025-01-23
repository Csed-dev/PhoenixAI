import ast

import astor
from phoenixai.utils.base_prompt_handling import save_code_to_file, trim_code,parse_ast, call_llm, read_file

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
            end_line = (
                node.body[-1].end_lineno
                if hasattr(node.body[-1], "end_lineno")
                else node.lineno
            )
            functions.append(
                {"name": node.name, "start_line": start_line, "end_line": end_line}
            )
    return functions


def extract_function_by_line(file_path, line_number):
    """Extrahiert eine Funktion basierend auf einer Zeilennummer."""
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    parsed_ast = ast.parse(code)

    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = (
                node.body[-1].end_lineno
                if hasattr(node.body[-1], "end_lineno")
                else start_line
            )
            if start_line <= line_number <= end_line:
                return astor.to_source(node).strip(), start_line, end_line

    raise ValueError(f"Keine Funktion in der Zeile {line_number} gefunden.")


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


def add_refactored_functions(lines, refactored_functions):
    """
    Fügt die refaktorierten Funktionen zum Code hinzu.

    Parameters:
    - lines (list of str): Die verbleibenden Zeilen des Codes.
    - refactored_functions (list of str): Eine Liste der refaktorierten Funktionsdefinitionen als Strings.

    Returns:
    - str: Der vollständige refaktorierte Code als String.
    """
    return "\n".join(lines) + "\n\n" + "\n\n".join(refactored_functions)


def save_refactored_code(file_path, refactored_functions, line_numbers):
    """
    Speichert den refaktorierten Code in einer neuen Datei.

    Parameters:
    - file_path (str): Der Pfad zur Originaldatei.
    - refactored_functions (list of str): Eine Liste der refaktorierten Funktionsdefinitionen als Strings.
    - line_numbers (list of int): Die Zeilennummern der Funktionen, die refaktoriert wurden.

    Returns:
    - str: Der Pfad zur gespeicherten refaktorierten Datei.
    """
    original_code = read_file(file_path)
    parsed_ast = parse_ast(original_code)
    lines = original_code.splitlines()
    lines_to_delete = identify_functions_to_remove(parsed_ast, line_numbers)
    updated_lines = remove_functions_from_code(lines, lines_to_delete)
    refactored_code = add_refactored_functions(updated_lines, refactored_functions)
    new_file_path = save_code_to_file(file_path, refactored_code)
    print(f"Der refaktorierte Code wurde in der Datei gespeichert: {new_file_path}")
    return new_file_path


def replace_function_in_code(lines, start_line, end_line, refactored_function):
    """Ersetzt die ursprüngliche Funktion durch die refaktorierte Version."""
    return lines[:start_line - 1] + [refactored_function] + lines[end_line:]


def process_refactoring(file_path, line_numbers):
    """Verarbeitet die Refaktorisierung der Funktionen an den angegebenen Zeilennummern."""
    try:
        original_code = read_file(file_path)
        lines = original_code.splitlines()

        # Sortiere Zeilennummern absteigend, um Änderungen rückwärts vorzunehmen
        sorted_line_numbers = sorted(line_numbers, reverse=True)

        for line_number in sorted_line_numbers:
            # Extrahiere die Funktion und ihre Position
            function_code, start_line, end_line = extract_function_by_line(file_path, line_number)

            # Generiere den Prompt und erhalte den refaktorierten Code
            prompt = generate_refactoring_prompt([function_code])
            refactored_code = call_llm(prompt)

            # Trim LLM-Antwort und validiere
            trimmed_refactored_code = trim_code(refactored_code)
            try:
                ast.parse(trimmed_refactored_code)
            except SyntaxError as e:
                raise RuntimeError(f"[Refactor] Syntaxfehler im LLM-Code: {e}")

            # Aktualisiere die Zeilen dynamisch
            lines = replace_function_in_code(lines, start_line, end_line, trimmed_refactored_code)

        # Speichere den Code nach der Refaktorisierung
        updated_code = "\n".join(lines)
        save_code_to_file(file_path, updated_code)

    except ValueError as e:
        print(f"[Refactor] Fehler beim Verarbeiten der Datei: {e}")
    except Exception as e:
        print(f"[Refactor] Unerwarteter Fehler: {e}")