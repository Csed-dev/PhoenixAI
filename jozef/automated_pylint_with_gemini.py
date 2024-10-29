import subprocess
import os
import json
import google.generativeai as genai

# Konfiguration für das KI-Modell (Setze hier deinen API-Schlüssel ein)
API_KEY = os.getenv("API_KEY")  # Sicherstellen, dass der API_KEY in der Umgebung gesetzt ist
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

def run_pylint(file_path):
    """Führt pylint für die ausgewählte Datei aus und gibt die Ausgabe zurück."""
    result = subprocess.run(['pylint', file_path], capture_output=True, text=True)
    return result.stdout

def get_gemini_suggestions(pylint_output):
    """Übermittelt den Pylint-Output an Gemini und erhält Optimierungsvorschläge."""
    prompt = f"""Analyze the following Pylint report and suggest improvements.
    Dont explain anything, just provide the improvements, so that I can copy it to my code:
    {pylint_output}
    """
    result = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="text/plain"
        )
    )
    return result.candidates[0].content.parts[0].text

def apply_suggestions(file_path, suggestions):
    """Schreibt die Optimierungen aus Gemini in eine neue Datei."""
    new_file_path = f"{os.path.splitext(file_path)[0]}_optimized.py"
    with open(file_path, 'r') as original_file, open(new_file_path, 'w') as new_file:
        new_file.write("# Optimizations based on Gemini's suggestions\n")
        new_file.write("# " + "\n# ".join(suggestions.splitlines()) + "\n\n")
        new_file.write(original_file.read())  # Hier wird der originale Code hinzugefügt, um echte Umsetzung zu simulieren
    return new_file_path

def main():
    # Schritt 1: Datei auswählen und ersten Pylint-Check durchführen
    file_path = input("Geben Sie den Namen der Datei ein, die mit Pylint getestet werden soll: ")
    if not os.path.exists(file_path):
        print(f"Datei '{file_path}' nicht gefunden.")
        return

    # Pylint vor der Umsetzung
    print("Führe ersten Pylint-Test durch...\n")
    initial_pylint_output = run_pylint(file_path)
    print("Pylint-Ergebnis vor der Umsetzung:\n", initial_pylint_output)

    # Pylint-Output an Gemini übergeben und Vorschläge erhalten
    print("Frage Gemini nach Verbesserungsvorschlägen...\n")
    gemini_suggestions = get_gemini_suggestions(initial_pylint_output)
    print("Gemini-Vorschläge:\n", gemini_suggestions)

    # Vorschläge anwenden und neue Datei erstellen
    print("Erstelle eine neue Datei mit den Vorschlägen von Gemini...\n")
    new_file_path = apply_suggestions(file_path, gemini_suggestions)

    # Pylint nach der Umsetzung
    print("Führe Pylint erneut auf der optimierten Datei aus...\n")
    final_pylint_output = run_pylint(new_file_path)
    print("Pylint-Ergebnis nach der Umsetzung:\n", final_pylint_output)

# Hauptprogramm ausführen
if __name__ == "__main__":
    main()
