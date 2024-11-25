import ast
import subprocess
import logging
import sqlite3
import re
import os
from typing import List, Tuple, Dict
from base_prompt_handling import generate_initial_prompt, call_llm, trim_code, save_code_to_file, extract_code_from_response
from test_multi_chain_comparison import MultiChainComparison

def setup_multichain_comparison(temperatures: List[float]) -> MultiChainComparison:
    """
    Erstellt und konfiguriert die MultiChainComparison-Instanz.
    """
    multi_chain = MultiChainComparison("", temperatures, "pylint")
    multi_chain.register_comparison_function("pylint", compare_pylint_results)
    return multi_chain

def analyze_with_pylint(file_path: str) -> Tuple[List[Dict[str, str]], str]:
    """
    Führt Pylint aus und generiert die formatierte Fehlerbeschreibung.
    """
    pylint_output = run_pylint(file_path)
    errors = extract_error_codes_and_messages(pylint_output)
    error_descriptions = build_error_report(errors)
    formatted_errors = format_errors_for_prompt(error_descriptions)
    return errors, formatted_errors


def should_stop_iteration(previous_error_count: int, current_error_count: int) -> bool:
    """
    Prüft, ob die Iteration gestoppt werden sollte basierend auf Fehleranzahl.
    """
    if previous_error_count is not None and current_error_count >= previous_error_count:
        logging.warning("Keine Verbesserung erkannt oder der Code wurde schlechter. Abbruch der Iterationen.")
        return True
    return False

def run_multichain_for_code_improvement(multi_chain: MultiChainComparison, code_content: str, formatted_errors: str) -> str:
    """
    Führt MultiChainComparison aus, um das beste Ergebnis basierend auf LLM-Antworten zu finden.
    """
    prompt = create_full_prompt(code_content, formatted_errors)
    multi_chain.prompt = prompt
    return multi_chain.run(call_llm)

def process_and_validate_code(improved_code: str, file_path: str, iteration: int) -> str:
    """
    Verarbeitet und validiert den vom LLM generierten Code.
    """
    trimmed_code = extract_code_from_response(improved_code)
    formatted_code = format_code_with_black(trimmed_code)

    if is_valid_python_code(formatted_code):
        save_code_to_file(file_path, formatted_code, iteration)
        logging.info(f"Verbesserter Code in Iteration {iteration} gespeichert.")
        return formatted_code
    else:
        logging.error("Der vom LLM zurückgegebene Code enthält Syntaxfehler.")
        return ""

def update_file_path(file_path: str, iteration: int) -> str:
    """
    Aktualisiert den Datei-Pfad für die nächste Iteration.
    """
    base_name, ext = os.path.splitext(file_path)
    return f"{base_name}_improved_{iteration}{ext}"

def compare_pylint_results(results: List[str], temperatures: List[float]) -> Tuple[int, str]:
    """
    Vergleicht Ergebnisse basierend auf dem Pylint-Score und wählt das beste aus.
    Zeigt den Pylint-Score für jede Temperatur an.

    :param results: Eine Liste von Code-Ergebnissen als Strings.
    :param temperatures: Eine Liste von Temperaturen, die den Ergebnissen entsprechen.
    :return: Ein Tupel aus Index und Code mit dem höchsten Pylint-Score.
    """
    scores = []
    for idx, result in enumerate(results):
        temp = temperatures[idx]

        # Bereinige den Code und speichere ihn in einer temporären Datei
        cleaned_code = trim_code(result)
        temp_file = save_to_temp_file(cleaned_code, idx)

        try:
            # Führe Pylint aus und extrahiere den Score
            pylint_output = run_pylint(temp_file)
            score = extract_pylint_score(pylint_output)
            scores.append((score, idx, cleaned_code))

            # Zeige den Pylint-Score für diese Temperatur an
            print(f"[Pylint-Workflow] Temperatur {temp}: Pylint-Score {score}/10")
        finally:
            # Entferne die temporäre Datei
            remove_temp_file(temp_file)

    # Wähle das Ergebnis mit dem höchsten Score
    return select_best_result(scores)

def save_to_temp_file(cleaned_code: str, idx: int) -> str:
    """
    Speichert den bereinigten Code in einer temporären Datei.

    :param cleaned_code: Der bereinigte Code als String.
    :param idx: Der Index der aktuellen Iteration.
    :return: Der Pfad zur temporären Datei.
    """
    temp_file = f"temp_file_{idx}.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(cleaned_code)
    return temp_file


def remove_temp_file(temp_file: str):
    """
    Entfernt die temporäre Datei, wenn sie existiert.

    :param temp_file: Der Pfad zur temporären Datei.
    """
    try:
        os.remove(temp_file)
    except Exception as e:
        logging.warning(f"Temp file konnte nicht gelöscht werden: {e}")


def select_best_result(scores: List[Tuple[float, int, str]]) -> Tuple[int, str]:
    """
    Wählt das Ergebnis mit dem höchsten Pylint-Score aus.

    :param scores: Eine Liste von Tupeln mit (Score, Index, Code).
    :return: Ein Tupel aus Index und Code des besten Ergebnisses.
    """
    best_result = max(scores, key=lambda x: x[0])  # x[0] ist der Score
    return best_result[1], best_result[2]  # Rückgabe von Index und Code

def extract_pylint_score(pylint_output: str) -> float:
    """
    Extrahiert den Pylint-Score aus der Ausgabe.
    :param pylint_output: Die vollständige Ausgabe von Pylint.
    :return: Der extrahierte Pylint-Score als Float.
    """
    try:
        # Suche nach dem Score-Format in der Pylint-Ausgabe
        match = re.search(r"Your code has been rated at (-?\d+\.\d+)/10", pylint_output)
        if match:
            return float(match.group(1))
        else:
            logging.warning("Pylint-Score konnte nicht extrahiert werden. Standardwert 0.0 wird verwendet.")
            return 0.0
    except Exception as e:
        logging.error(f"Fehler beim Extrahieren des Pylint-Scores: {e}")
        return 0.0
    
def format_code_with_black(code):
    """Formatiert den Code mit Black."""
    temp_file = "temp_code.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(code)

    subprocess.run(['black', temp_file])

    with open(temp_file, "r", encoding="utf-8") as f:
        formatted_code = f.read()

    os.remove(temp_file)
    return formatted_code

def is_valid_python_code(code_str):
    try:
        ast.parse(code_str)
        return True
    except SyntaxError as e:
        logging.error(f"Syntaxfehler im Code: {e}")
        return False

# Pylint ausführen
def run_pylint(file_path):
    """Führt Pylint aus und gibt die Roh-Ausgabe zurück."""
    result = subprocess.run(['pylint', file_path], capture_output=True, text=True)
    return result.stdout

# Fehlercodes extrahieren
def extract_error_codes_and_messages(pylint_output):
    """Extrahiert die Fehlercodes und zugehörigen Nachrichten aus der Pylint-Ausgabe."""
    matches = re.findall(r": ([A-Z]\d{4}): (.+?)(?:\n|$)", pylint_output)
    return [{"error_code": match[0], "message_emitted": match[1]} for match in matches]


# Fehlerbeschreibung aus der Datenbank abrufen
def fetch_error_description_from_db(error_code):
    """Holt die Fehlerbeschreibung aus der Datenbank."""
    db_path = "phoenixai/database/code_quality_tests.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT description
        FROM pylint_test
        WHERE error_code = ?
    """, (error_code,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

# Fehlercodes mit Beschreibungen anreichern
def build_error_report(errors):
    """Kombiniert Fehler-ID, Nachricht und Beschreibung zu einer Liste."""
    descriptions = []
    for error in errors:
        description = fetch_error_description_from_db(error["error_code"])
        if description:
            descriptions.append(
                f"- {error['error_code']} ({error['message_emitted']}): {description}"
            )
        else:
            descriptions.append(
                f"- {error['error_code']} ({error['message_emitted']}): Beschreibung nicht gefunden"
            )
    return descriptions

# Fehlerdetails formatieren
def format_errors_for_prompt(error_descriptions):
    """Formatiert die Fehlerdetails für den LLM-Prompt."""
    return "\n".join(error_descriptions)

# LLM-Prompt erstellen
def create_full_prompt(code_content, formatted_errors):
    """Erstellt den vollständigen Prompt für das LLM."""
    # print(generate_initial_prompt(code_content) + formatted_errors)
    return generate_initial_prompt(code_content) + formatted_errors

def iterative_process_with_pylint(file_path, code_content, iterations):
    """
    Führt den gesamten Workflow iterativ durch, basierend auf der angegebenen Anzahl von Iterationen.
    Nutzt MultiChainComparison, um den besten Prompt basierend auf verschiedenen Temperaturen zu wählen.
    """
    logging.basicConfig(level=logging.INFO)

    # MultiChainComparison Setup
    temperatures = [0.2, 0.4, 0.6]
    multi_chain = setup_multichain_comparison(temperatures)

    previous_error_count = None

    for i in range(1, iterations + 1):
        logging.info(f"--- Iteration {i}/{iterations} gestartet ---")

        errors, formatted_errors = analyze_with_pylint(file_path)
        if not errors:
            logging.info("Keine Fehlercodes gefunden. Workflow abgeschlossen.")
            break

        current_error_count = len(errors)
        if should_stop_iteration(previous_error_count, current_error_count):
            break
        previous_error_count = current_error_count

        improved_code = run_multichain_for_code_improvement(multi_chain, code_content, formatted_errors)
        if not improved_code.strip():
            logging.error(f"Keine valide Antwort vom LLM in Iteration {i}. Abbruch.")
            break

        formatted_code = process_and_validate_code(improved_code, file_path, i)
        if formatted_code:
            code_content = formatted_code
            file_path = update_file_path(file_path, i)
        else:
            break

    logging.info("Iterativer Workflow abgeschlossen.")
