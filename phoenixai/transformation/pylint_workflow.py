import ast
import subprocess
import logging
import sqlite3
import re
import os
from typing import List, Tuple
from base_prompt_handling import generate_initial_prompt, call_llm, trim_code, save_code_to_file, extract_code_from_response
from test_multi_chain_comparison import MultiChainComparison

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

# Hauptfunktion: Workflow
def process_file_with_pylint(file_path, code_content):
    """
    Führt den gesamten Workflow mit Pylint durch.
    """
    # Schritt 1: Pylint ausführen
    pylint_output = run_pylint(file_path)

    # Schritt 2: Fehlercodes und Nachrichten extrahieren
    errors = extract_error_codes_and_messages(pylint_output)

    if not errors:
        print("Keine Fehlercodes gefunden.")
        return None

    # Schritt 3: Beschreibungen abrufen
    error_descriptions = build_error_report(errors)

    # Schritt 4: Fehlerdetails formatieren
    formatted_errors = format_errors_for_prompt(error_descriptions)

    # Schritt 5: Prompt erstellen
    prompt = create_full_prompt(code_content, formatted_errors)

    # Schritt 6: LLM aufrufen
    improved_code = call_llm(prompt)

    # Schritt 7: Code trimmen
    trimmed_code = trim_code(improved_code)

    # Schritt 8: Code speichern
    save_path = save_code_to_file(file_path, trimmed_code, 1)
    print(f"Verbesserter Code gespeichert unter: {save_path}")
    return trimmed_code

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
        # Bereinige den LLM-Output
        cleaned_code = trim_code(result)

        temp_file = f"temp_file_{idx}.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(cleaned_code)

        # Führe Pylint aus und extrahiere den Score
        pylint_output = run_pylint(temp_file)
        score = extract_pylint_score(pylint_output)
        scores.append((score, idx, cleaned_code))

        # Entferne die temporäre Datei
        try:
            os.remove(temp_file)
        except Exception as e:
            logging.warning(f"Temp file konnte nicht gelöscht werden: {e}")

        # Zeige den Pylint-Score für diese Temperatur an
        print(f"Temperatur {temp}: Pylint-Score {score}/10")

    # Wähle das Ergebnis mit dem höchsten Score
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

def iterative_process_with_pylint(file_path, code_content, iterations):
    """
    Führt den gesamten Workflow iterativ durch, basierend auf der angegebenen Anzahl von Iterationen.
    Nutzt MultiChainComparison, um den besten Prompt basierend auf verschiedenen Temperaturen zu wählen.
    """
    logging.basicConfig(level=logging.INFO)
    previous_error_count = None

    # MultiChainComparison Setup
    temperatures = [0.1, 0.2, 0.3]
    multi_chain = MultiChainComparison("", temperatures, "pylint")
    multi_chain.register_comparison_function("pylint", compare_pylint_results)

    for i in range(1, iterations + 1):
        logging.info(f"--- Iteration {i}/{iterations} gestartet ---")

        # Schritt 1: Pylint ausführen und Fehlercodes und Nachrichten extrahieren
        pylint_output = run_pylint(file_path)
        errors = extract_error_codes_and_messages(pylint_output)

        if not errors:
            logging.info("Keine Fehlercodes gefunden. Workflow abgeschlossen.")
            break

        # Schritt 2: Fehlerbeschreibungen abrufen
        error_descriptions = build_error_report(errors)
        formatted_errors = format_errors_for_prompt(error_descriptions)

        # Fehleranzahl validieren
        current_error_count = len(errors)
        logging.info(f"Pylint-Fehler gefunden: {current_error_count}")
        if previous_error_count is not None and current_error_count >= previous_error_count:
            logging.warning("Keine Verbesserung erkannt oder der Code wurde schlechter. Abbruch der Iterationen.")
            break
        previous_error_count = current_error_count

        # Schritt 3: MultiChainComparison verwenden
        prompt = create_full_prompt(code_content, formatted_errors)
        multi_chain.prompt = prompt
        improved_code = multi_chain.run(call_llm)
        if not improved_code.strip():
            logging.error(f"Keine valide Antwort vom LLM in Iteration {i}. Abbruch.")
            break

        # Schritt 4: Code trimmen und aktualisieren
        trimmed_code = extract_code_from_response(improved_code)
        formatted_code = format_code_with_black(trimmed_code)

        # Schritt 5: Syntaxüberprüfung
        if is_valid_python_code(formatted_code):
            # Code speichern
            save_path = save_code_to_file(file_path, formatted_code, i)
            logging.info(f"Verbesserter Code in Iteration {i} gespeichert unter: {save_path}")

            # Aktualisiere code_content und file_path für die nächste Iteration
            code_content = formatted_code
            file_path = save_path
        else:
            logging.error("Der vom LLM zurückgegebene Code enthält Syntaxfehler.")
            # Optional: Entscheiden, ob der Workflow fortgesetzt werden soll
            break

    logging.info("Iterativer Workflow abgeschlossen.")
