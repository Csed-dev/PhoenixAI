import os
import subprocess
import requests
from github import Github
from dotenv import load_dotenv
import google.generativeai as genai

# Lade die .env Datei
load_dotenv()

# Zugriff auf den GitHub Token und das Original-Repo
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
ORIGINAL_REPO = os.getenv('ORIGINAL_REPO').strip("/")
g = Github(GITHUB_TOKEN)

def configure_genai_api():
    """Konfiguriert die Gemini API mit dem API-Schlüssel."""
    # Setze den API-Schlüssel (API_KEY) für die Gemini API
    API_KEY = os.getenv('API_KEY')  # Der API-Key sollte in der .env Datei gesetzt sein
    
    if not API_KEY:
        raise ValueError("Der API-Schlüssel ist nicht gesetzt. Bitte setzen Sie die Umgebungsvariable 'API_KEY'.")
    
    # Gemini API konfigurieren
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')

# Gemini-Modell initialisieren
model = configure_genai_api()

def create_fork():
    """Erstellt einen Fork des GitHub Repositories und gibt den Fork-Repo-Namen zurück."""
    try:
        repo = g.get_repo(ORIGINAL_REPO)
        print(f"Repository gefunden: {repo.full_name}")
        
        # Fork erstellen
        forked_repo = repo.create_fork()
        print(f'Fork erstellt: {forked_repo.html_url}')
        return forked_repo.full_name
    except Exception as e:
        print(f"Fehler beim Zugriff auf das Repository: {e}")
        return None

FORKED_REPO = create_fork()

def clone_fork():
    """Klonen des Forks, falls das Verzeichnis nicht existiert."""
    repo_name = FORKED_REPO.split('/')[-1]
    if not os.path.exists(repo_name):
        subprocess.run(['git', 'clone', f'https://github.com/{FORKED_REPO}.git'])
        print(f'Fork {FORKED_REPO} geklont.')
    else:
        print(f"Verzeichnis '{repo_name}' existiert bereits. Klonen übersprungen.")

def get_project_files(repo_path):
    """Liest nur Textdateien aus dem Repository und gibt sie als Liste von Strings zurück."""
    project_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(('.py')):  # Nur Textdateien einlesen
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        project_files.append(file_content)
                except Exception as e:
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
    except Exception as e:
        print(f"Fehler beim Abrufen des Projektüberblicks: {e}")

# Hauptskript
if __name__ == '__main__':
    create_fork()
    if FORKED_REPO:
        clone_fork()

    # Pfad zum geklonten Repository
    repo_path = './' + FORKED_REPO.split('/')[-1]

    # Schritt 2: Projektüberblick erstellen
    get_project_overview(repo_path)
