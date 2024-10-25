"""
Dieses Modul analysiert die Abhängigkeiten zwischen Dateien in einem GitHub-Repository.
"""

import os
import json
import google.generativeai as genai
import typing_extensions as typing
import networkx as nx
import matplotlib.pyplot as plt
from repo_copy_and_overview import get_project_files
from dotenv import load_dotenv

# Konstanten für Pfad und Modell-Setup
REPO_PATH = "Quizcraft"  # Pfad zum kopierten Repository-Verzeichnis

# Lade die .env Datei und API-Schlüssel
load_dotenv()
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY nicht gesetzt. Bitte .env-Datei überprüfen.")

# Konfiguriere das GenerativeAI-Modell mit dem API-Schlüssel
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Definiere die Struktur für die Rückgabe der Abhängigkeiten
class Edge(typing.TypedDict):
    """Repräsentiert eine Abhängigkeit zwischen zwei Dateien."""
    source: str
    target: str

class DependencyGraph(typing.TypedDict):
    """Repräsentiert den Graphen der Abhängigkeiten mit Knoten und Kanten."""
    nodes: list[str]
    edges: list[Edge]

# Verwende get_project_files, um die Dateien im 'Quizcraft'-Verzeichnis zu laden
code_files = get_project_files(REPO_PATH)
if not code_files:
    print("Keine relevanten Dateien gefunden.")
else:
    # Modellaufruf zur Analyse der Abhängigkeiten im Repository
    PROMPT = (
        "Analyze the dependencies between files in the 'Quizcraft' GitHub repository. "
        "Return the analysis in the form of nodes and edges. "
        f"The files: {code_files}"
    )
    result = model.generate_content(
        PROMPT,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=DependencyGraph
        ),
    )

    # Extrahiere den JSON-Inhalt als String
    response_content = result.candidates[0].content.parts[0].text
    print(response_content)

    # JSON-String zu einem Dictionary konvertieren
    response = json.loads(response_content)

    # Prüfe das Ergebnis und konvertiere es in einen Graphen
    if "nodes" in response and "edges" in response:
        # Erstelle den Graphen
        G = nx.DiGraph()  # Gerichteter Graph für Abhängigkeiten
        G.add_nodes_from(response["nodes"])
        for edge in response["edges"]:
            G.add_edge(edge["source"], edge["target"])

        # Graph-Darstellung mit verbessertem Layout und Parametern
        plt.figure(figsize=(12, 10))
        pos = nx.shell_layout(G)  # Layout für bessere Lesbarkeit

        # Zeichne den Graphen mit angepassten Stilen
        nx.draw(G, pos, with_labels=True, node_size=500, width=0.8, font_size=8, 
                node_color="skyblue", edge_color="gray", font_color="darkblue", font_weight="bold")

        plt.title("Übersichtlicher Dependency Graph des 'Quizcraft' Repository")
        plt.show()
    else:
        print("Ungültige Antwort erhalten:", response)
