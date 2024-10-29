"""
Dieses Modul analysiert ein lokales Repository und erstellt den AST für jede Datei,
sowie eine in JSON gespeicherte Analyse mithilfe eines generativen KI-Modells.
"""

import os
import json
import ast
import google.generativeai as genai
import typing_extensions as typing

# Konfiguriere Gemini mit dem API-Schlüssel
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Definiere das Antwortformat für die Analyse
class FileAnalysis(typing.TypedDict):
    """Struktur zur Speicherung der Analyse einer Datei mit Zweck und Abhängigkeiten."""
    filename: str
    purpose: str
    dependencies: list[str]

class RepoAnalysis(typing.TypedDict):
    """Struktur zur Speicherung der Repository-Analyse mit Übersicht und Dateien."""
    overview: str
    files: list[FileAnalysis]

def analyze_repo(repo_path):
    """
    Analysiert Python-Dateien in einem Repository und speichert die Analyse als JSON.
    
    Args:
        repo_path (str): Pfad zum Repository-Verzeichnis.
    """
    code_files = [os.path.join(repo_path, f) for f in os.listdir(repo_path) if f.endswith('.py')]
    prompt = (
        "Analyze the following Python files from the repository. "
        "Provide an overview, purpose, and dependencies.\n\n"
        f"{code_files}"
    )

    result = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=RepoAnalysis
        ),
    )

    response_content = result.candidates[0].content.parts[0].text
    response_data = json.loads(response_content)
    with open("repo_analysis.json", "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=4)
    print("Analyse gespeichert in 'repo_analysis.json'")

def parse_and_show_ast(repo_path):
    """
    Erstellt und zeigt den AST für jede Python-Datei im Repository an und speichert ihn als JSON.
    
    Args:
        repo_path (str): Pfad zum Repository-Verzeichnis.
    """
    code_files = [os.path.join(repo_path, f) for f in os.listdir(repo_path) if f.endswith('.py')]
    ast_data = {}

    for file_path in code_files:
        if os.path.isfile(file_path):  # Prüft, ob es sich um eine Datei handelt
            print(f"\nAST für Datei: {file_path}")
            with open(file_path, 'r', encoding="utf-8") as file:
                source_code = file.read()

            # Erzeuge den AST des Codes
            tree = ast.parse(source_code)
            ast_json = ast_to_json(tree)
            ast_data[file_path] = ast_json  # Speichert den AST als JSON

            # Ausgabe des AST im Terminal (optional)
            print(json.dumps(ast_json, indent=4))

    # Speichern des gesamten AST als JSON-Datei
    output_file = os.path.join(repo_path, "ast_data.json")
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(ast_data, json_file, indent=4)
        print("Laufende AST-Daten wurden in 'ast_data.json' gespeichert.")
    print(f"AST wurde als JSON in '{output_file}' gespeichert.")

def ast_to_json(node):
    """
    Konvertiert einen AST-Knoten rekursiv in ein JSON-freundliches Format.
    
    Args:
        node (ast.AST): Der zu konvertierende AST-Knoten.
    
    Returns:
        dict: JSON-kompatibles Dictionary, das den AST repräsentiert.
    """
    if isinstance(node, ast.AST):
        result = {"_type": node.__class__.__name__}
        for field, value in ast.iter_fields(node):
            result[field] = ast_to_json(value)
        return result
    if isinstance(node, list):
        return [ast_to_json(n) for n in node]
    return node


def main():
    """
    Hauptfunktion, die das Repository analysiert und den AST für jede Datei erstellt.
    """
    # Pfad zum lokal geklonten Repository (ersetze mit deinem Verzeichnisnamen)
    repo_path = './Quizcraft'

    # Schritt 1: Analyse des Repositories und Speichern des Ergebnisses
    print("Starte die Analyse des Repositories mit Gemini...")
    analyze_repo(repo_path)
    print("Analyse abgeschlossen und in 'repo_analysis.json' gespeichert.")

    # Schritt 2: AST für jede Datei im Repository erstellen und anzeigen
    print("\nErstelle und zeige den AST für jede Datei an...")
    parse_and_show_ast(repo_path)
    print("\nAST-Visualisierung abgeschlossen.")

# Ausführen des Hauptprogramms
if __name__ == '__main__':
    main()
