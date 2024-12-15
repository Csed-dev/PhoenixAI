import logging
import os
import subprocess
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

"""This module provides functions to improve Python code using a large language model (LLM).

It reads Python code from a file, sends it to the LLM for improvement,
and saves the improved code back to a file.  The module also includes
functions for formatting the code with Black and sorting imports with isort.
"""


def read_file(file_path):
    """Reads Python code from a file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        str: The content of the file.

    Raises:
        FileNotFoundError: If the file does not exist."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_llm_model(model_name: str = "gemini-1.5-flash"):
    """Loads the specified LLM model.

    Args:
        model_name (str, optional): The name of the LLM model to load. Defaults to "gemini-1.5-flash".

    Returns:
        google.generativeai.GenerativeModel: The loaded LLM model.

    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not set."""
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY nicht gesetzt. Bitte setzen Sie die Umgebungsvariable."
        )
    genai.configure(api_key=gemini_api_key)
    return genai.GenerativeModel(model_name)


def generate_initial_prompt(code_content):
    """Generates the initial prompt for the LLM.

    Args:
        code_content (str): The Python code to be improved.

    Returns:
        str: The initial prompt for the LLM."""
    return f"""
Code:

{code_content}

Gib **nur** den verbesserten **reinen Code** zurück, ohne zusätzliche Erklärungen, 
Kommentare oder Markdown-Codeblöcke (wie ```python). Der Code sollte direkt 
ausgeführt werden können. Beachte, dass jede Datei einen Docstring benötigt.
Bitte verbessere den Python-Code, indem du die angegebenen Probleme behebst:

Zu behebende Probleme:
"""


def call_llm(prompt: str, temperature: float = 0.7) -> str:
    """Calls the LLM (Gemini) with a given prompt and temperature.

    Args:
        prompt (str): The input prompt for the LLM.
        temperature (float, optional): The creativity of the LLM. Defaults to 0.7.

    Returns:
        str: The generated output of the LLM."""
    try:
        model = load_llm_model()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature),
        )
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        logging.error("Keine validen Ergebnisse vom LLM erhalten.")
        return ""
    except Exception as e:
        logging.error(f"Fehler beim Aufrufen des LLM: {e}")
        return ""


def _strip_code_start(improved_code):
    """Removes Markdown markers from the beginning of the code."""
    lines = improved_code.splitlines()
    while lines and lines[0].strip() in ("```python", "```"):
        lines.pop(0)
    return "\n".join(lines).strip()


def _strip_code_end(improved_code):
    """Removes everything after the last Markdown marker ```."""
    lines = improved_code.splitlines()
    last_markdown_index = next(
        (
            len(lines) - 1 - idx
            for idx, line in enumerate(reversed(lines))
            if line.strip() == "```"
        ),
        None,
    )
    if last_markdown_index is None:
        return "\n".join(lines).strip()
    return "\n".join(lines[:last_markdown_index]).strip()


def trim_code(improved_code):
    """Combines the two strip functions to completely trim the code."""
    code = _strip_code_start(improved_code)
    code = _strip_code_end(code)
    return code


def save_code_to_file(file_path, improved_code, iteration=None):
    """Saves the improved code to a file.

    Args:
        file_path (str): The path to the original file.
        improved_code (str): The improved code to be saved.
        iteration (int, optional): The iteration number. If provided, a new file is created.

    Returns:
        str: The path to the saved file."""
    if iteration is not None:
        base_name, ext = os.path.splitext(file_path)
        new_file_path = f"{base_name}_improved_{iteration}{ext}"
    else:
        new_file_path = file_path
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(improved_code)
    print(f"[Save] Code gespeichert unter: {new_file_path}")
    return new_file_path


def format_file_with_black(file_path):
    """Formats the given Python file using Black.

    Args:
        file_path (Union[str, Path]): The path to the file to be formatted. Can be a string or a Path object.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError: If formatting with Black fails.
    """
    file = Path(file_path)
    if not file.is_file():
        raise FileNotFoundError(
            f"Die angegebene Datei existiert nicht: {file.resolve()}"
        )
    try:
        subprocess.run(
            ["black", str(file)],
            check=True,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"[Black ]Die Datei {file.resolve()} wurde erfolgreich formatiert.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"""Fehler beim Formatieren der Datei mit Black: {file.resolve()}.
Black-Ausgabe:
{e.stderr}"""
        ) from e


def apply_isort_to_file(file_path):
    """Applies isort to the given file to sort imports.

    Args:
        file_path (Union[str, Path]): The path to the file to be formatted. Can be a string or a Path object.

    Raises:
        FileNotFoundError: If the file does not exist.
        RuntimeError: If sorting with isort fails.
    """
    file = Path(file_path)
    if not file.is_file():
        raise FileNotFoundError(
            f"Die angegebene Datei existiert nicht: {file.resolve()}"
        )
    try:
        subprocess.run(
            ["isort", str(file)],
            check=True,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"[Isort] Die Datei {file.resolve()} wurde erfolgreich bearbeitet.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"""Fehler beim Anwenden von isort auf die Datei: {file.resolve()}.
isort-Ausgabe:
{e.stderr}"""
        ) from e


def run_black_and_isort(file_path):
    try:
        format_file_with_black(file_path)
        apply_isort_to_file(file_path)
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Formatieren mit isort oder Black: {e}")
