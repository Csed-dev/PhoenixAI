import os
import subprocess
import sqlite3
import re
from collections import OrderedDict
import google.generativeai as genai

# Laden des Gemini API-Schlüssels und Konfiguration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY nicht gesetzt. Bitte setzen Sie die Umgebungsvariable.")
genai.configure(api_key=gemini_api_key)

# Funktion: Pylint ausführen und Fehlercodes extrahieren
def run_pylint(file_path):
    """Führt Pylint für eine angegebene Datei aus und extrahiert Fehlercodes."""
    result = subprocess.run(['pylint', file_path], capture_output=True, text=True)
    error_codes = re.findall(r": ([A-Z]\d{4}):", result.stdout)
    return error_codes, result.stdout

# Funktion: Fehlerdetails aus der SQLite-Datenbank abrufen
def fetch_error_details_from_db(error_code):
    """Holt die Fehlerbeschreibung und die Korrektur aus der Datenbank."""
    db_path = "phoenixai/database/code_quality_tests.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT description, problematic_code, correct_code
        FROM pylint_test
        WHERE error_code = ?
    """, (error_code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        description, problematic_code, correct_code = result
        return {
            "error_code": error_code,
            "description": description,
            "problematic_code": problematic_code,
            "correct_code": correct_code
        }
    else:
        return None

# Funktion: Verbesserung des Codes mithilfe von Gemini
def improve_code_with_gemini(code_content, errors):
    """Verbessert den Code basierend auf Fehlerdetails und gibt den verbesserten Code zurück."""

    # Fehlerdetails formatieren und Duplikate entfernen
    unique_errors = []
    seen_descriptions = set()
    for error in errors:
        desc = error['description']
        if desc not in seen_descriptions:
            seen_descriptions.add(desc)
            unique_errors.append(error)

    formatted_errors = "\n".join(
        f"- {error['description']}" for error in unique_errors
    )

    # Prompt erstellen
    prompt = f"""
Bitte verbessere den folgenden Python-Code, indem du die angegebenen Probleme behebst und sicherstellst, dass der Code den PEP8-Richtlinien entspricht.

Code:

{code_content}

Zu behebende Probleme:
{formatted_errors}

Gib nur den verbesserten Code zurück, ohne zusätzliche Erklärungen oder Kommentare.
"""

    # Aufruf des Gemini-Modells
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
    response = model.generate_content([prompt])

    # Zugriff auf den generierten Code
    try:
        improved_code = response.candidates[0].content.parts[0].text
    except (AttributeError, IndexError) as e:
        print("Fehler beim Zugriff auf den generierten Code:", e)
        improved_code = ""

    # --- Bereinigung des Codes ---
    # Entfernen von unerwünschtem Text vor `import`, `def`, `class` oder `#`
    lines = improved_code.splitlines()
    start_index = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith(('import', 'from', 'def', 'class', '#', '"""')):
            start_index = idx
            break

    # Entfernen von unerwünschtem Text am Ende, wie ``` oder andere Markdown-Syntax
    end_index = len(lines)
    for idx, line in enumerate(reversed(lines), 1):
        if not line.strip() or line.strip() == "```":
            end_index = len(lines) - idx
        else:
            break

    # Trimmen und Neuaufbau des Codes
    trimmed_code = '\n'.join(lines[start_index:end_index + 1]).strip()
    return trimmed_code

# Funktion: Verbesserte Datei speichern
def save_improved_code(file_path, improved_code, iteration):
    """Speichert den verbesserten Code in einer neuen Datei."""
    base_name, ext = os.path.splitext(file_path)
    new_file_path = f"{base_name}_improved_{iteration}{ext}"
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(improved_code)
    return new_file_path

# Hauptprogramm
def main():
    # Datei auswählen
    original_file_path = "phoenixai/repo_management/manage_legacy_repo.py"
    if not os.path.exists(original_file_path):
        print(f"Datei '{original_file_path}' nicht gefunden.")
        return

    current_file_path = original_file_path  # Aktueller Dateipfad

    for iteration in range(1, 6):
        print(f"\n=== Iteration {iteration} ===")

        # Den Codeinhalt aus der aktuellen Datei einlesen
        with open(current_file_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        # Schritt 1: Pylint ausführen und Fehlercodes extrahieren
        print("Führe Pylint aus...")
        error_codes, pylint_output = run_pylint(current_file_path)
        print("Gefundene Fehlercodes:", error_codes)

        # Pylint-Ergebnis ausgeben
        print("Pylint-Ergebnis:\n", pylint_output)

        # Schritt 2: Fehlerdetails aus der Datenbank abrufen
        error_details_list = []
        unique_error_codes = list(OrderedDict.fromkeys(error_codes))
        for error_code in unique_error_codes:
            error_details = fetch_error_details_from_db(error_code)
            if error_details:
                error_details_list.append(error_details)

        if not error_details_list:
            print("Keine Fehlerdetails gefunden oder keine Fehler mehr vorhanden.")
            break

        # Schritt 3: Verbesserter Code generieren
        print("Generiere verbesserten Code mithilfe von Gemini...")
        improved_code = improve_code_with_gemini(code_content, error_details_list)

        # Ausgabe des verbesserten Codes
        # print("\n=== Verbesserter Code ===")
        # print(improved_code)

        # Schritt 4: Verbesserte Datei speichern
        print("Speichere die verbesserte Datei...")
        new_file_path = save_improved_code(original_file_path, improved_code, iteration)
        print(f"Verbesserte Datei gespeichert unter: {new_file_path}")

        # Aktualisiere den Dateipfad für die nächste Iteration
        current_file_path = new_file_path

    print("\nAlle Iterationen abgeschlossen.")

# Programm ausführen
if __name__ == "__main__":
    main()
