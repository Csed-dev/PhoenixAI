"""
Dieses Modul erstellt einen Fork eines GitHub-Repositories, klont es lokal und analysiert die Projektdateien,
um einen Überblick über die Projektstruktur zu erhalten.
"""

import os
import subprocess
from github import Github
from dotenv import load_dotenv
import google.generativeai as genai

# Lade die .env Datei
load_dotenv()

# Zugriff auf den GitHub Token und das Original-Repo
github_token = os.getenv('GITHUB_TOKEN')
original_repo = os.getenv('ORIGINAL_REPO').strip("/")
g = Github(github_token)

def configure_genai_api():
    """Konfiguriert die Gemini API mit dem API-Schlüssel."""
    api_key = os.getenv('API_KEY')  # Der API-Key sollte in der .env Datei gesetzt sein
    
    if not api_key:
        raise ValueError("Der API-Schlüssel ist nicht gesetzt. Bitte setzen Sie die Umgebungsvariable 'API_KEY'.")
    
    # Gemini API konfigurieren
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# Gemini-Modell initialisieren
model = configure_genai_api()

def create_fork():
    """Erstellt einen Fork des GitHub Repositories und gibt den Fork-Repo-Namen zurück."""
    try:
        repo = g.get_repo(original_repo)
        print(f"Repository gefunden: {repo.full_name}")
        
        # Fork erstellen
        forked_repo = repo.create_fork()
        print(f'Fork erstellt: {forked_repo.html_url}')
        return forked_repo.full_name
    except g.GithubException as e:
        print(f"Fehler beim Zugriff auf das Repository: {e}")
        return None

forked_repo = create_fork()

def clone_fork():
    """Klonen des Forks, falls das Verzeichnis nicht existiert."""
    repo_name = forked_repo.split('/')[-1]
    if not os.path.exists(repo_name):
        subprocess.run(['git', 'clone', f'https://github.com/{forked_repo}.git'], check=True)
        print(f'Fork {forked_repo} geklont.')
    else:
        print(f"Verzeichnis '{repo_name}' existiert bereits. Klonen übersprungen.")

def get_project_files(repo_path):
    """Liest nur Textdateien aus dem Repository und gibt sie als Liste von Strings zurück."""
    project_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.py'):  # Nur Textdateien einlesen
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        project_files.append(file_content)
                except (IOError, UnicodeDecodeError) as e:
                    print(f"Fehler beim Lesen von {file_path}: {e}")
    return project_files

def get_project_overview(repo_path):
    """Sendet die Projektdateien an Gemini und gibt einen Überblick über das Projekt zurück."""
    code_files = get_project_files(repo_path)
    if not code_files:
        print("Keine relevanten Dateien gefunden.")
        return

    # Erstelle den Prompt für Gemini
    prompt = (
        f"Hier ist eine Liste von Dateien aus einem Projekt. Erstelle einen kurzen Überblick über das Projekt, "
        f"inklusive Hauptfunktionalitäten, Struktur und Zweck. Der Text:\n\n{code_files}\n"
    )
    try:
        response = model.generate_content(prompt)
        print("Projektüberblick erhalten:")
        print(response)
    except Exception as e:  # spezifische Ausnahme wählen, falls möglich
        print(f"Fehler beim Abrufen des Projektüberblicks: {e}")

# Hauptskript
if __name__ == '__main__':
    if forked_repo:
        clone_fork()

    # Pfad zum geklonten Repository
    repo_path = './' + forked_repo.split('/')[-1]

    # Schritt 2: Projektüberblick erstellen
    get_project_overview(repo_path)
