import os
import subprocess
import sqlite3
import re
from dspy import LM, Signature, InputField, OutputField, ChainOfThought
import dspy  # Für die Konfiguration von DSPy
from dspy.adapters import ChatAdapter


# Laden des Gemini API-Schlüssels
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Konfiguration des LM
lm = LM(
    model="gemini/gemini-pro",
    api_key=gemini_api_key,
    temperature=0.5,
    max_tokens=3000
)

# DSPy konfigurieren
dspy.settings.configure(lm=lm)

# Definition der Signatur für die Codeverbesserung
class CodeImprovement(Signature):
    """Verbessert den gegebenen Code basierend auf Fehlerbeschreibungen."""
    code: str = InputField(desc="Der zu verbessernde Quellcode.")
    errors: str = InputField(desc="Die Beschreibung der gefundenen Fehler.")
    reasoning: str = OutputField(desc="Die Überlegungen zur Verbesserung des Codes.")
    improved_code: str = OutputField(desc="Der verbesserte Quellcode.")

# Erstellung des DSPy-Moduls für die Codeverbesserung mit ChainOfThought
improve_code_module = ChainOfThought(CodeImprovement, adapter=ChatAdapter())

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
            "description": description,
            "problematic_code": problematic_code,
            "correct_code": correct_code
        }
    else:
        return None

# Funktion: Verbesserung des Codes mithilfe von DSPy und ChainOfThought
def improve_code_with_dspy(file_path, errors):
    """Verbessert den Code basierend auf Fehlerdetails und gibt den verbesserten Code zurück."""
    with open(file_path, "r", encoding="utf-8") as f:
        file_code = f.read()

    # Fehlerdetails formatieren
    formatted_errors = "\n\n".join(
        f"""Problem Description: {error['description']}
        Example Problematic Code: {error['problematic_code']}
        Example Correct Code: {error['correct_code']}
        """ for error in errors
            )

    # Verwendung des DSPy-Moduls zur Codeverbesserung mit ChainOfThought
    result = improve_code_module(
        code=file_code,
        errors=formatted_errors
    )

    # Überlegungen und verbesserten Code extrahieren
    reasoning = result.reasoning
    improved_code = result.improved_code

    # Optional: Prompt ausgeben
    print("\n=== Gesendeter Prompt ===")
    lm.inspect_history(n=1)  # Zeigt den letzten generierten Prompt

    # Optional: Überlegungen ausgeben
    print("\n=== Überlegungen des Modells ===")
    print(reasoning)

    return improved_code

# Funktion: Verbesserte Datei speichern
def save_improved_code(file_path, improved_code):
    """Speichert den verbesserten Code in einer neuen Datei."""
    new_file_path = f"{os.path.splitext(file_path)[0]}_improved.py"
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(improved_code)
    return new_file_path

# Hauptprogramm
def main():
    # Datei auswählen
    file_path = "phoenixai/repo_management/managa_legacy_repo.py"
    if not os.path.exists(file_path):
        print(f"Datei '{file_path}' nicht gefunden.")
        return

    # Schritt 1: Pylint ausführen und Fehlercodes extrahieren
    print("Führe Pylint aus...")
    error_codes, pylint_output = run_pylint(file_path)
    print("Gefundene Fehlercodes:", error_codes)

    # Schritt 2: Fehlerdetails aus der Datenbank abrufen
    error_details_list = []
    for error_code in error_codes:
        error_details = fetch_error_details_from_db(error_code)
        if error_details:
            error_details_list.append(error_details)

    if not error_details_list:
        print("Keine Fehlerdetails gefunden. Abbruch.")
        return

    # Schritt 3: Verbesserter Code generieren
    print("Generiere verbesserten Code mithilfe von DSPy und ChainOfThought...")
    improved_code = improve_code_with_dspy(file_path, error_details_list)

    # Schritt 4: Verbesserte Datei speichern
    print("Speichere die verbesserte Datei...")
    new_file_path = save_improved_code(file_path, improved_code)
    print(f"Verbesserte Datei gespeichert unter: {new_file_path}")

    # Schritt 5: Pylint erneut ausführen
    print("Führe Pylint auf der verbesserten Datei aus...")
    pylint_output_after = run_pylint(new_file_path)[1]
    print("Pylint-Ergebnis nach der Verbesserung:\n", pylint_output_after)

# Programm ausführen
if __name__ == "__main__":
    main()
