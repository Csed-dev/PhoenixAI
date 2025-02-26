"""
Flask-basierte Webanwendung zur Anzeige von Analyse-Ergebnissen

Dieses Modul stellt eine Webanwendung bereit, die als Bestandteil des Gesamtsystems
von PhoenixAI genutzt wird. Die Anwendung liest Report-Dateien aus dem Reports-Verzeichnis
und zeigt diese in einer übersichtlichen HTML-Oberfläche an. Das Modul enthält keine
eigenständige Ausführung (kein if __main__), sondern wird von einem WSGI-Server oder
aus der GUI heraus gestartet.
"""

import os
import json
import urllib.parse
import markdown
from flask import Flask, request, abort, render_template_string

app = Flask(__name__)

# Basisverzeichnis und Reports-Verzeichnis ermitteln
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "..", "reports")

# Jinja2-Filter für URL-Kodierung
app.jinja_env.filters['url_encode'] = lambda value: urllib.parse.quote(value)

# HTML-Vorlage für die Detailansicht eines Reports
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <p><a href="/">Zurück zur Übersicht</a></p>
    <title>Analyse Report: {{ report_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        .content { background-color: #f4f4f4; padding: 1em; border-radius: 5px; }
        a { text-decoration: none; color: blue; }
    </style>
</head>
<body>
    <h1>Analyse Report: {{ report_name }}</h1>
    <div class="content">
        {{ report_content|safe }}
    </div>
</body>
</html>
"""

# HTML-Vorlage für die Indexseite (Übersicht aller Reports)
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Analyse Reports Übersicht</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        ul { list-style: none; padding: 0; }
        li { margin: 0.5em 0; }
        a { text-decoration: none; color: blue; }
    </style>
</head>
<body>
    <h1>Analyse Reports Übersicht</h1>
    <ul>
        {% for report in reports %}
            <li><a href="/view_report?report={{ report | url_encode }}">{{ report }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""


def get_report_structure():
    """
    Durchläuft das REPORTS_DIR und erstellt eine verschachtelte Struktur:

    {
      "Name_Checker": {
          "datei1": [report1, report2, ...],
          "datei2": [report1, ...]
      },
      "Performance": {
          "datei1": [report1, ...]
      },
      ...
    }

    Dabei werden nur Unterordner berücksichtigt, die eine Analyse repräsentieren.
    """
    structure = {}
    # Erste Ebene: Analyse-Typen
    for analysis_type in os.listdir(REPORTS_DIR):
        analysis_path = os.path.join(REPORTS_DIR, analysis_type)
        if os.path.isdir(analysis_path):
            structure[analysis_type] = {}
            # Zweite Ebene: Dateinamen (Unterordner)
            for file_dir in os.listdir(analysis_path):
                file_dir_path = os.path.join(analysis_path, file_dir)
                if os.path.isdir(file_dir_path):
                    # Dritte Ebene: Report-Dateien (Versionen)
                    reports = [f for f in os.listdir(file_dir_path)
                               if os.path.isfile(os.path.join(file_dir_path, f))]
                    reports.sort()  # Sortierung anhand des Dateinamens (Version + Timestamp)
                    structure[analysis_type][file_dir] = reports
    return structure


# Aktualisierte HTML-Vorlage für die Indexseite
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Analyse Reports Übersicht</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        h2 { color: #333; }
        ul { list-style: none; padding: 0; }
        li { margin: 0.5em 0; }
        a { text-decoration: none; color: blue; }
    </style>
</head>
<body>
    <h1>Analyse Reports Übersicht</h1>
    {% for analysis_type, files in report_structure.items() %}
        <h2>{{ analysis_type }}</h2>
        <ul>
            {% for file, reports in files.items() %}
                <li>
                    <strong>{{ file }}</strong>
                    <ul>
                        {% for report in reports %}
                            <li>
                                <a href="/view_report?report={{ (analysis_type + '/' + file + '/' + report) | url_encode }}">{{ report }}</a>
                            </li>
                        {% endfor %}
                    </ul>
                </li>
            {% endfor %}
        </ul>
    {% endfor %}
</body>
</html>
"""

@app.route("/")
def index():
    if not os.path.isdir(REPORTS_DIR):
        return "Reports-Verzeichnis nicht gefunden.", 404
    report_structure = get_report_structure()
    return render_template_string(INDEX_TEMPLATE, report_structure=report_structure)

@app.route("/view_report")
def view_report():
    # Verwende nun den Parameter "report" statt "id"
    report_rel_path = request.args.get("report")
    if not report_rel_path:
        abort(400, "Kein Report angegeben.")

    # Dekodiere den relativen Pfad
    report_rel_path = urllib.parse.unquote(report_rel_path)
    # Erzeuge den vollständigen Pfad zum Report, basierend auf REPORTS_DIR
    report_path = os.path.join(REPORTS_DIR, report_rel_path)
    # Sicherheitscheck: Der Report muss innerhalb des REPORTS_DIR liegen
    if not os.path.abspath(report_path).startswith(os.path.abspath(REPORTS_DIR)):
        abort(403, "Zugriff verweigert.")
    if not os.path.isfile(report_path):
        abort(404, "Report nicht gefunden.")

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        abort(500, f"Fehler beim Lesen des Reports: {e}")

    # Konvertiere den Markdown-Inhalt in HTML
    html_content = markdown.markdown(content)
    return render_template_string(REPORT_TEMPLATE, report_name=report_rel_path, report_content=html_content)




if __name__ == "__main__":
    # Starte die Flask-Anwendung im Debug-Modus auf Port 5000
    app.run(debug=True, port=5000)
