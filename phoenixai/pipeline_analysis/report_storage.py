import os
import datetime
import uuid
import json

def save_report_generic(report_content, analysis_type, target_file_path):
    """
    Speichert den Report in einer hierarchischen Verzeichnisstruktur:

      reports/
          <Analysis_Type>/
              <Dateiname ohne Extension>/
                  <analysis_type>_report_v<version>_<timestamp>.md

    Zusätzlich wird ein eindeutiger Report-ID generiert und in einer Mapping-Datei gespeichert.
    Die Mapping-Datei (report_mapping.json) speichert eine Zuordnung von Report-ID zu
    dem relativen Pfad der Report-Datei.
    """
    # Basis-Reports-Verzeichnis (eine Ebene oberhalb dieses Moduls)
    base_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    analysis_dir = os.path.join(base_reports_dir, analysis_type)
    if not os.path.exists(analysis_dir):
        os.makedirs(analysis_dir)

    # Bestimme den Basisnamen der analysierten Datei (ohne Erweiterung)
    file_base = os.path.splitext(os.path.basename(target_file_path))[0]
    file_report_dir = os.path.join(analysis_dir, file_base)
    if not os.path.exists(file_report_dir):
        os.makedirs(file_report_dir)

    # Erstelle einen einheitlichen Präfix für den Report-Dateinamen
    prefix = f"{analysis_type.lower()}_report"
    # Bestimme die nächste Versionsnummer basierend auf vorhandenen Reports
    existing_files = [f for f in os.listdir(file_report_dir) if f.startswith(prefix)]
    version = len(existing_files) + 1

    # Erzeuge den Zeitstempel
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Erzeuge den neuen Report-Namen
    new_report_filename = f"{prefix}_v{version}_{timestamp}.md"
    new_report_path = os.path.join(file_report_dir, new_report_filename)

    # Falls report_content eine Liste ist, in einen String umwandeln
    if isinstance(report_content, list):
        report_str = "\n".join(report_content)
    else:
        report_str = report_content

    # Füge den Zeitstempel als Überschrift in den Report ein
    header = f"**Analyse durchgeführt am:** {timestamp}\n\n"
    report_str = header + report_str

    with open(new_report_path, "w", encoding="utf-8") as f:
        f.write(report_str)

    print(f"Report gespeichert unter: {new_report_path}")

    # Generiere eine eindeutige Report-ID und aktualisiere die Mapping-Datei
    report_id = str(uuid.uuid4())
    mapping_file = os.path.join(base_reports_dir, "report_mapping.json")
    mapping = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, "r", encoding="utf-8") as mf:
            try:
                mapping = json.load(mf)
            except json.JSONDecodeError:
                mapping = {}
    # Speichere den relativen Pfad (relativ zum base_reports_dir)
    relative_path = os.path.relpath(new_report_path, base_reports_dir)
    mapping[report_id] = relative_path
    with open(mapping_file, "w", encoding="utf-8") as mf:
        json.dump(mapping, mf, ensure_ascii=False, indent=4)

    print(f"Report-ID: {report_id}")
    return report_id
