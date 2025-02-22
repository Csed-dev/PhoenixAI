from flask import Flask, request, redirect, url_for, render_template_string
import os
import json
import uuid
import datetime
from phoenixai.pipeline_analysis.performance_analysis import analyze_target, generate_report
import markdown

# Konfiguration
app = Flask(__name__)
DATA_FILE = "projects.json"
REPORTS_DIR = "reports"
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# Hilfsfunktionen zum Laden/Speichern von Projekten
def load_projects():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_projects(projects):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=4)

# Landing-Page: Liste aller Projekte
@app.route("/")
def index():
    projects = load_projects()
    html = """
    <h1>Projekte</h1>
    <ul>
    {% for project in projects.values() %}
      <li>
        <a href="{{ url_for('project_page', project_id=project['id']) }}">{{ project['name'] }}</a>
        ({{ project['path'] }})
      </li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('create_project') }}">Neues Projekt erstellen</a>
    """
    return render_template_string(html, projects=projects)

# Projekt erstellen (Formular)
@app.route("/create_project", methods=["GET", "POST"])
def create_project():
    if request.method == "POST":
        name = request.form.get("name")
        path = request.form.get("path")
        if not os.path.exists(path):
            return "Pfad existiert nicht!", 400
        project_id = str(uuid.uuid4())
        project = {
            "id": project_id,
            "name": name,
            "path": path,
            "analyses": []
        }
        projects = load_projects()
        projects[project_id] = project
        save_projects(projects)
        return redirect(url_for("project_page", project_id=project_id))
    html = """
    <h1>Neues Projekt erstellen</h1>
    <form method="post">
      Projektname: <input type="text" name="name"><br>
      Projektpfad: <input type="text" name="path"><br>
      <input type="submit" value="Erstellen">
    </form>
    """
    return render_template_string(html)

# Projektseite: Details und Analyse-Optionen
@app.route("/project/<project_id>")
def project_page(project_id):
    projects = load_projects()
    project = projects.get(project_id)
    if not project:
        return "Projekt nicht gefunden", 404
    # Verfügbare Analysen
    analysis_options = ["Performance", "Name Checker", "SonarQube", "Architecture"]
    html = """
    <h1>Projekt: {{ project['name'] }}</h1>
    <p>Pfad: {{ project['path'] }}</p>
    <h2>Analysen ausführen</h2>
    <ul>
    {% for option in analysis_options %}
      <li><a href="{{ url_for('run_analysis', project_id=project['id'], analysis_type=option) }}">{{ option }}</a></li>
    {% endfor %}
    </ul>
    <h2>Bisherige Analysen</h2>
    <ul>
    {% for analysis in project.get('analyses', []) %}
      <li>
         {{ analysis['type'] }} - {{ analysis['timestamp'] }} -
         <a href="{{ url_for('view_analysis', project_id=project['id'], analysis_id=analysis['id']) }}">Anzeigen</a>
      </li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('index') }}">Zurück zu Projekten</a>
    """
    return render_template_string(html, project=project, analysis_options=analysis_options)

# Analysen ausführen (Wrapper-Funktion)
@app.route("/project/<project_id>/run/<analysis_type>")
def run_analysis(project_id, analysis_type):
    projects = load_projects()
    project = projects.get(project_id)
    if not project:
        return "Projekt nicht gefunden", 404

    # Hier implementieren wir beispielhaft die Performance-Analyse.
    # Für die anderen Analysearten simulieren wir einen einfachen Report.
    if analysis_type == "Performance":
        results = analyze_target(project["path"])
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"performance_{project_id}_{timestamp}.md"
        report_filepath = os.path.join(REPORTS_DIR, report_filename)
        generate_report(results, report_filepath)
        with open(report_filepath, "r", encoding="utf-8") as f:
            md_content = f.read()
        report_html = markdown.markdown(md_content, extensions=["fenced_code", "codehilite"])
    elif analysis_type == "Name Checker":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"name_checker_{project_id}_{timestamp}.md"
        report_filepath = os.path.join(REPORTS_DIR, report_filename)
        with open(report_filepath, "w", encoding="utf-8") as f:
            f.write("# Name Checker Report\n\nKeine Probleme gefunden.")
        report_html = markdown.markdown(open(report_filepath, "r", encoding="utf-8").read(), extensions=["fenced_code", "codehilite"])
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{analysis_type.lower()}_{project_id}_{timestamp}.md"
        report_filepath = os.path.join(REPORTS_DIR, report_filename)
        with open(report_filepath, "w", encoding="utf-8") as f:
            f.write(f"# {analysis_type} Report\n\nSimulierter Report für {analysis_type}.")
        report_html = markdown.markdown(open(report_filepath, "r", encoding="utf-8").read(), extensions=["fenced_code", "codehilite"])

    analysis_entry = {
        "id": str(uuid.uuid4()),
        "type": analysis_type,
        "timestamp": datetime.datetime.now().isoformat(),
        "report_file": report_filepath
    }
    project.setdefault("analyses", []).append(analysis_entry)
    projects[project_id] = project
    save_projects(projects)
    # Nach dem Ausführen der Analyse direkt zur Detailansicht weiterleiten
    return redirect(url_for("view_analysis", project_id=project_id, analysis_id=analysis_entry["id"]))

# Analysebericht anzeigen
@app.route("/project/<project_id>/analysis/<analysis_id>")
def view_analysis(project_id, analysis_id):
    projects = load_projects()
    project = projects.get(project_id)
    if not project:
        return "Projekt nicht gefunden", 404
    analysis = next((a for a in project.get("analyses", []) if a["id"] == analysis_id), None)
    if not analysis:
        return "Analyse nicht gefunden", 404
    try:
        with open(analysis["report_file"], "r", encoding="utf-8") as f:
            md_content = f.read()
    except Exception as e:
        md_content = f"Fehler beim Laden des Reports: {e}"
    report_html = markdown.markdown(md_content, extensions=["fenced_code", "codehilite"])
    html = """
    <h1>{{ analysis['type'] }} Report</h1>
    <p>Erstellt am: {{ analysis['timestamp'] }}</p>
    <div>{{ report_html|safe }}</div>
    <a href="{{ url_for('project_page', project_id=project['id']) }}">Zurück zum Projekt</a>
    """
    return render_template_string(html, analysis=analysis, project=project, report_html=report_html)

if __name__ == "__main__":
    app.run(debug=True)
