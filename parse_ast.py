import os
import subprocess
from github import Github
from dotenv import load_dotenv
import google.generativeai as genai
import typing_extensions as typing
import json
import ast

# Konfiguriere Gemini mit dem API-Schlüssel
API_KEY = os.getenv('API_KEY')
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Definiere das Antwortformat für die Analyse
class FileAnalysis(typing.TypedDict):
    filename: str
    purpose: str
    dependencies: list[str]

class RepoAnalysis(typing.TypedDict):
    overview: str
    files: list[FileAnalysis]

def analyze_repo(repo_path):
    code_files = [os.path.join(repo_path, f) for f in os.listdir(repo_path) if f.endswith('.py')]
    prompt = f"Analyze the following Python files from the repository. Provide an overview, purpose, and dependencies.\n\n{code_files}"
    
    result = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=RepoAnalysis
        ),
    )
    
    response_content = result.candidates[0].content.parts[0].text
    response_data = json.loads(response_content)
    with open("repo_analysis.json", "w") as f:
        json.dump(response_data, f, indent=4)
    print("Analyse gespeichert in 'repo_analysis.json'")

def parse_and_show_ast(repo_path):
    code_files = [os.path.join(repo_path, f) for f in os.listdir(repo_path) if f.endswith('.py')]
    ast_data = {}

    for file_path in code_files:
        if os.path.isfile(file_path):  # Prüft, ob es sich um eine Datei handelt
            print(f"\nAST für Datei: {file_path}")
            with open(file_path, 'r') as file:
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
    """Konvertiert einen AST-Knoten rekursiv in ein JSON-freundliches Format."""
    if isinstance(node, ast.AST):
        result = {"_type": node.__class__.__name__}
        for field, value in ast.iter_fields(node):
            result[field] = ast_to_json(value)
        return result
    elif isinstance(node, list):
        return [ast_to_json(n) for n in node]
    else:
        return node


def main():
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
