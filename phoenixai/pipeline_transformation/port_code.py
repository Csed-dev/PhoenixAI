

import os
from phoenixai.utils.base_prompt_handling import (
    read_file,
    trim_code,
    call_llm,
    save_code_to_file,
)


def generate_porting_prompt(code):
    """
    Erstellt einen Prompt für das LLM, um alten Code in Python 3 zu portieren.

    Args:
        code (str): Der Originalcode, z. B. in Python 2 oder einer anderen Sprache.

    Returns:
        str: Der generierte Prompt.
    """
    return f"""
{code}

### Aufgabe:
Portiere den obigen Code so, dass er in Python 3 vollständig ausführbar ist. Achte darauf, dass
- die ursprüngliche Funktionalität und Semantik erhalten bleibt,
- eventuelle veraltete Syntax oder Bibliotheken durch moderne Alternativen ersetzt werden,
- die alten Funktionsnamen erhalten bleiben, damit die Schnittschtelle sich nicht ändert.
Du kannst neue Funktionen erstellen, die dann in der alten Funktion gebraucht werden.
Dadurch dient die alte Funktions nur noch als Wrapper. Beachte dabei, dass der Funktionalität erhalten bleiben soll,
- der Code direkt ausführbar ist, ohne dass zusätzliche Anpassungen notwendig sind.

Gib **nur** den portierten, lauffähigen Python 3 Code zurück, ohne zusätzliche Erklärungen oder Kommentare.
    """


def run_porting(file_path):
    """
    Führt den Portierungsvorgang für die angegebene Datei durch:
      - Liest den Originalcode,
      - generiert einen Portierungsprompt,
      - ruft das LLM zur Portierung auf,
      - trimmt und speichert den neuen Code zurück in die Datei.

    Args:
        file_path (str): Der Pfad zur zu portierenden Datei.
    """
    print(f"[Porting] Portierung für {file_path} wird gestartet.")
    try:
        original_code = read_file(file_path)
    except Exception as e:
        print(f"[Porting] Fehler beim Lesen der Datei: {e}")
        return

    prompt = generate_porting_prompt(original_code)
    print("[Porting] Sende Prompt an das LLM ...")
    improved_code = call_llm(prompt)
    if not improved_code:
        print("[Porting] LLM hat keine Antwort geliefert.")
        return

    trimmed_code = trim_code(improved_code)
    save_code_to_file(file_path, trimmed_code)
