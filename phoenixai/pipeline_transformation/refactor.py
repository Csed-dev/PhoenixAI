"""
This module provides functions for refactoring Python code using a large language model (LLM).

It allows users to identify functions to refactor, generate prompts for an LLM,
and integrate the LLM's refactored code into the original file.
"""

import ast
import astor
from phoenixai.utils.base_prompt_handling import (
    save_code_to_file,
    trim_code,
    parse_ast,
    call_llm,
    read_file,
)


def extract_functions(file_path):
    """Extracts all functions from a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        list of dict: A list of dictionaries, each containing 'name', 'start_line', and 'end_line' for each function.
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
    """Extracts a function based on a line number.

    Args:
        file_path (str): The path to the Python file.
        line_number (int): The line number of the function.

    Returns:
        tuple: The function code (str), start line (int), and end line (int).

    Raises:
        ValueError: If no function is found at the specified line number."""
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
    """Generates the prompt for the LLM.

    Args:
        functions (list of str): A list of function codes.

    Returns:
        str: The prompt for the LLM."""
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
    """Identifies functions to remove based on the given line numbers.

    Args:
        parsed_ast (ast.AST): The parsed AST of the original code.
        line_numbers (list of int): The line numbers of the functions that were refactored.

    Returns:
        set of int: The indices of the lines to remove."""
    lines_to_delete = set()
    for node in parsed_ast.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1
            end_line = (
                node.body[-1].end_lineno - 1
                if hasattr(node.body[-1], "end_lineno")
                else start_line
            )
            if any(start_line <= line - 1 <= end_line for line in line_numbers):
                lines_to_delete.update(range(start_line, end_line + 1))
    return lines_to_delete


def remove_functions_from_code(lines, lines_to_delete):
    """Removes the specified lines from the code.

    Args:
        lines (list of str): The lines of the original code.
        lines_to_delete (set of int): The indices of the lines to remove.

    Returns:
        list of str: The remaining lines after removal."""
    return [line for idx, line in enumerate(lines) if idx not in lines_to_delete]


def add_refactored_functions(lines, refactored_functions):
    """Adds the refactored functions to the code.

    Args:
        lines (list of str): The remaining lines of the code.
        refactored_functions (list of str): A list of the refactored function definitions as strings.

    Returns:
        str: The complete refactored code as a string."""
    return "\n".join(lines) + "\n\n" + "\n\n".join(refactored_functions)


def save_refactored_code(file_path, refactored_functions, line_numbers):
    """Saves the refactored code to a new file.

    Args:
        file_path (str): The path to the original file.
        refactored_functions (list of str): A list of the refactored function definitions as strings.
        line_numbers (list of int): The line numbers of the functions that were refactored.

    Returns:
        str: The path to the saved refactored file."""
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
    """Replaces the original function with the refactored version.

    Args:
        lines (list of str): The lines of code.
        start_line (int): The starting line number of the original function.
        end_line (int): The ending line number of the original function.
        refactored_function (str): The refactored function code.

    Returns:
        list of str: The updated lines of code."""
    return lines[: start_line - 1] + [refactored_function] + lines[end_line:]


def process_refactoring(file_path, line_numbers):
    """Processes the refactoring of functions at the specified line numbers.

    Args:
        file_path (str): The path to the file.
        line_numbers (list of int): The line numbers of the functions to refactor."""
    try:
        original_code = read_file(file_path)
        lines = original_code.splitlines()
        sorted_line_numbers = sorted(line_numbers, reverse=True)
        for line_number in sorted_line_numbers:
            function_code, start_line, end_line = extract_function_by_line(
                file_path, line_number
            )
            prompt = generate_refactoring_prompt([function_code])
            refactored_code = call_llm(prompt)
            trimmed_refactored_code = trim_code(refactored_code)
            try:
                ast.parse(trimmed_refactored_code)
            except SyntaxError as e:
                raise RuntimeError(f"[Refactor] Syntaxfehler im LLM-Code: {e}")
            lines = replace_function_in_code(
                lines, start_line, end_line, trimmed_refactored_code
            )
        updated_code = "\n".join(lines)
        save_code_to_file(file_path, updated_code)
    except ValueError as e:
        print(f"[Refactor] Fehler beim Verarbeiten der Datei: {e}")
    except Exception as e:
        print(f"[Refactor] Unerwarteter Fehler: {e}")
