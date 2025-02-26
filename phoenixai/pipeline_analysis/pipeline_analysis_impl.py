import os
import subprocess

from phoenixai.pipeline_analysis.name_checker import NameChecker
from phoenixai.pipeline_analysis.performance_analysis import analyze_target, generate_report


def run_analyze_arch(file_path):
    print(f"[Analysis] Architektur-Analyse auf: {file_path}")

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports", "Architecture")
    os.makedirs(output_path, exist_ok=True)

    output_file = os.path.join(output_path, "module_dependencies.svg")

    try:
        result = subprocess.run(["python", "-m", "pydeps", file_path, "-o", output_file, "--max-bacon=2"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        if result.returncode == 0:
            print(f"[Analysis] Pydeps erfolgreich ausgeführt. Graph gespeichert unter {output_file}")
        else:
            print(f"[Analysis] Fehler bei pydeps: {result.stderr}")

    except FileNotFoundError:
        print("[Error] Pydeps wurde nicht gefunden. Installiere es mit `pip install pydeps`.")

def run_script2(file_path):
    print(f"[Analysis] Skript 2 auf: {file_path}")

def run_name_checker(file_path):
    print(f"[Analysis] NameChecker auf: {file_path}")
    checker = NameChecker(file_path)
    checker.generate_report()
    # Nutze die neue Schnittstelle; save_report gibt die Report-ID zurück.
    report_id = checker.save_report()
    print(f"[Analysis] Report gespeichert mit ID: {report_id}")
    return f"Report: {report_id}"



def run_script4(file_path):
    print(f"[Analysis] Skript 4 auf: {file_path}")


def run_performance_analysis(file_path: str):
    """
    Führt die Performance-Analyse für die gegebene Datei durch und speichert den Report
    in einer hierarchischen Verzeichnisstruktur:

      reports/
          Performance/
              <Dateiname ohne Extension>/
                  performance_report_v<version>_<timestamp>.md

    Anschließend wird der Report über die Flask-Anwendung angezeigt.
    """
    import datetime, os
    print(f"[Analysis] Performance-Analyse auf: {file_path}")
    results = analyze_target(file_path)

    # Erzeuge den Pfad zum Reports-Verzeichnis
    base_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(base_dir, "..", "reports", "Performance")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    # Erzeuge einen Unterordner für die analysierte Datei (ohne Extension)
    file_base = os.path.splitext(os.path.basename(file_path))[0]
    file_report_dir = os.path.join(reports_dir, file_base)
    if not os.path.exists(file_report_dir):
        os.makedirs(file_report_dir)

    # Bestimme die nächste Versionsnummer basierend auf vorhandenen Reports
    existing_files = [f for f in os.listdir(file_report_dir) if f.startswith("performance_report")]
    version = len(existing_files) + 1

    # Erzeuge den Zeitstempel
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Erzeuge den neuen Report-Namen
    report_filename = f"performance_report_v{version}_{timestamp}.md"
    report_path = os.path.join(file_report_dir, report_filename)

    generate_report(results, report_path)
    print(f"[Analysis] Report gespeichert unter: {report_path}")

analysis_actions = {
    "Name Checker": run_name_checker,
    "SonarQube": run_script4,
    "Performance": run_performance_analysis,
    "Architecture": run_analyze_arch,
}
