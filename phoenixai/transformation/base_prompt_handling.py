import logging
import os
import re
import subprocess
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv


def load_llm_model(model_name: str = "gemini-1.5-flash"):
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY nicht gesetzt. Bitte setzen Sie die Umgebungsvariable."
        )
    genai.configure(api_key=gemini_api_key)
    return genai.GenerativeModel(model_name)


def generate_initial_prompt(code_content):
    """Erstellt den Basisprompt für das LLM."""
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
    """
    Ruft das LLM (Gemini) mit einem bestimmten Prompt und einer spezifischen Temperatur auf.

    :param prompt: Der Eingabeprompt für das LLM.
    :param temperature: Die Kreativität des LLMs (Standard: 0.7).
    :return: Die generierte Ausgabe des LLMs.
    """
    try:
        # Anfrage senden
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                # candidate_count=1,  # Eine Ausgabe erzeugen
                temperature=temperature,
            ),
        )

        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        logging.error("Keine validen Ergebnisse vom LLM erhalten.")
        return ""

    except Exception as e:
        logging.error(f"Fehler beim Aufrufen des LLM: {e}")
        return ""


def _strip_code_start(improved_code):
    """Entfernt Markdown-Markierungen"""
    lines = improved_code.splitlines()

    # Entferne ```python oder ``` nur am Anfang des Codes
    while lines and lines[0].strip() in ("```python", "```"):
        lines.pop(0)

    return "\n".join(lines).strip()


def _strip_code_end(improved_code):
    """Entfernt alles, was nach der letzten Markdown-Markierung ``` kommt."""
    lines = improved_code.splitlines()

    last_markdown_index = next(
        (
            len(lines) - 1 - idx
            for idx, line in enumerate(reversed(lines))
            if line.strip() == "```"
        ),
        None,
    )
    # Wenn keine Markdown-Markierung gefunden wurde, bleibt der Code unverändert
    if last_markdown_index is None:
        return "\n".join(lines).strip()

    # Schneide alles ab der letzten Markdown-Markierung
    return "\n".join(lines[:last_markdown_index]).strip()


def trim_code(improved_code):
    """Kombiniert die beiden Strip-Funktionen, um den Code vollständig zu trimmen."""
    code = _strip_code_start(improved_code)
    code = _strip_code_end(code)
    return code
  

def save_code_to_file(file_path, improved_code, iteration=None):
    """
    Speichert den verbesserten Code in einem festgelegten Ordner.
    
    Parameters:
    - file_path (str): Der Pfad zur Originaldatei.
    - improved_code (str): Der verbesserte Code, der gespeichert werden soll.
    - iteration (int, optional): Die Iterationsnummer. Wenn nicht angegeben, wird kein Suffix hinzugefügt.
    
    Returns:
    - str: Der Pfad zur gespeicherten Datei.
    """
    # Zielordner definieren
    output_dir = os.path.join("phoenixai", "transformation", "improved_codes")
    os.makedirs(output_dir, exist_ok=True)  # Ordner erstellen, falls er nicht existiert

    # Originaldateiname ohne bereits existierende Suffixe "_improved_X"
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    if "_improved_" in base_name:
        base_name = base_name.split("_improved_")[0]

    # Neuer Dateiname mit oder ohne Iterationsnummer im Zielordner
    if iteration is not None:
        new_file_name = f"{base_name}_improved_{iteration}{ext}"
    else:
        new_file_name = f"{base_name}_improved{ext}"

    new_file_path = os.path.join(output_dir, new_file_name)

    # Datei schreiben
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(improved_code)

    return new_file_path



def format_file_with_black(file_path):
    """
    Formatiert die angegebene Python-Datei mit Black.

    :param file_path: Der Pfad zur Datei, die formatiert werden soll.

    :raises FileNotFoundError: Wenn die Datei nicht existiert.
    :raises RuntimeError: Wenn die Formatierung mit Black fehlschlägt.
    """
    file = Path(file_path)
    if not file.is_file():
        raise FileNotFoundError(
            f"Die angegebene Datei existiert nicht: {file.resolve()}"
        )

    try:
        # Black auf die Datei anwenden
        subprocess.run(
            ["black", str(file)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Die Datei {file.resolve()} wurde erfolgreich mit Black formatiert.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Fehler beim Formatieren der Datei mit Black: {file.resolve()}.\n"
            f"Black-Ausgabe:\n{e.stderr}"
        ) from e


def apply_isort_to_file(file_path):
    """
    Wendet isort auf die angegebene Datei an, um die Importe zu sortieren.

    :param file_path: Der Pfad zur Datei, die formatiert werden soll.

    :raises FileNotFoundError: Wenn die Datei nicht existiert.
    :raises RuntimeError: Wenn das Sortieren mit isort fehlschlägt.
    """
    file = Path(file_path)
    if not file.is_file():
        raise FileNotFoundError(
            f"Die angegebene Datei existiert nicht: {file.resolve()}"
        )

    try:
        # isort auf die Datei anwenden
        subprocess.run(
            ["isort", str(file)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Die Datei {file.resolve()} wurde erfolgreich mit isort bearbeitet.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Fehler beim Anwenden von isort auf die Datei: {file.resolve()}.\n"
            f"isort-Ausgabe:\n{e.stderr}"
        ) from e
