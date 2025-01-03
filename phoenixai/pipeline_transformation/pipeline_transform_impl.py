import time

import os

from phoenixai.pipeline_transformation.add_docstrings import process_file_for_docstrings
from phoenixai.utils.base_prompt_handling import apply_isort_to_file, format_file_with_black
from phoenixai.pipeline_transformation.imports_sort import collect_imports_and_format
from phoenixai.pipeline_transformation.pylint_workflow import iterative_process_with_pylint
from phoenixai.pipeline_transformation.refactor import process_refactoring,extract_functions
from phoenixai.pipeline_transformation.sourcery_quick_fix import run_sourcery_fix
from phoenixai.pipeline_transformation.typ_annotation_updater import annotation_process_file


class PipelineStep:
    def __init__(self, name, function, *args, **kwargs):
        """
        Repräsentiert einen einzelnen Schritt in der Pipeline.

        :param name: Der Name des Schritts.
        :param function: Die Funktion, die ausgeführt wird.
        :param args: Positionale Argumente für die Funktion.
        :param kwargs: Schlüsselwortargumente für die Funktion.
        """
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.status = "Pending"
        self.duration = None  # Hinzugefügtes Attribut für die Dauer

    def run(self):
        """Führt den Schritt aus und aktualisiert den Status und die Dauer."""
        try:
            start_time = time.time()
            self.function(*self.args, **self.kwargs)
            end_time = time.time()
            self.duration = end_time - start_time
            self.status = "🟢 Success"
        except Exception as e:
            self.duration = None
            self.status = f"🔴 Failed: {e}"


class Pipeline:
    def __init__(self, treeview):
        """
        Repräsentiert die Pipeline, die eine Reihe von Schritten in Reihenfolge ausführt.

        :param treeview: Das Treeview-Widget, das die Pipeline-Schritte darstellt.
        """
        self.steps = []
        self.current_step = 0
        self.treeview = treeview

    def add_step(self, name, function, *args, **kwargs):
        """
        Fügt einen neuen Schritt zur Pipeline hinzu.

        :param name: Der Name des Schritts.
        :param function: Die auszuführende Funktion.
        :param args: Positionale Argumente.
        :param kwargs: Schlüsselwortargumente.
        """
        step = PipelineStep(name, function, *args, **kwargs)
        self.steps.append(step)
        self.display_status()

    def display_status(self):
        """Aktualisiert die Treeview mit den aktuellen Status- und Dauerinformationen."""
        # Zuerst alle bestehenden Einträge löschen
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Dann alle Schritte erneut einfügen mit aktualisierten Status und Dauer
        for idx, step in enumerate(self.steps, start=1):
            duration_text = f"{step.duration:.2f}s" if step.duration else "N/A"
            self.treeview.insert(
                "",
                "end",
                iid=str(idx),
                values=(step.status, step.name, self.args_or_default(step), duration_text)
            )

    def args_or_default(self, step):
        if step.args:
            full_path = step.args[0]
            parts = full_path.split(os.sep)

            # Wenn es mehr als 4 Teile gibt (z.B. ['home', 'user', 'projekt', 'unterordner', 'datei.py']),
            # dann zeige nur die letzten 4 Segmente (3 Ordner + Dateiname).
            # Bei weniger wird nichts verändert.
            if len(parts) > 4:
                truncated_path = os.path.join(*parts[-4:])
            else:
                truncated_path = full_path

            return truncated_path
        else:
            return "N/A"

    def run_next_step(self):
        """
        Führt den nächsten Schritt in der Pipeline aus.
        Zeigt eine Informationsmeldung an, wenn alle Schritte abgeschlossen sind.
        """
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            step.status = "Running..."
            self.display_status()
            self.treeview.update_idletasks()

            step.run()
            self.display_status()
            self.current_step += 1

    def reset(self):
        """Setzt die Pipeline zurück."""
        self.steps = []
        self.current_step = 0
        self.display_status()


def run_pylint(file_path):
    """Führt Pylint aus und gibt die Ergebnisse aus."""
    with open(file_path, "r", encoding="utf-8") as f:
        code_content = f.read()
    iterative_process_with_pylint(file_path, code_content, 1)

def run_sonarqube(file_path):
    """Führt SonarQube-Analyse aus (Platzhalter für echte Integration)."""
    print(f"[Pipeline] SonarQube wird ausgeführt für: {file_path}")
    # Hier könnte die SonarQube CLI oder eine API-Integration implementiert werden


def run_black(file_path):
    """Formatiert die Datei mit Black."""
    format_file_with_black(file_path)


def run_isort(file_path):
    """Sortiert die Importe in der Datei mit isort."""
    apply_isort_to_file(file_path)


def move_imports(file_path):
    """Sortiert und verschiebt die Imports in der Datei."""
    print(f"[Pipeline] Importe werden für {file_path} verschoben und formatiert.")
    collect_imports_and_format(file_path)


def run_refactor(file_path, line_numbers=None):
    if line_numbers is None:
        line_numbers = []

    if not line_numbers:
        # Wenn keine line_numbers angegeben, alle Funktionen ermitteln
        all_funcs = extract_functions(file_path)
        line_numbers = [func['start_line'] for func in all_funcs]

    print(f"[Pipeline] Refactor wird ausgeführt für: {file_path} mit Funktionen in Zeilen {line_numbers}")
    process_refactoring(file_path, line_numbers=line_numbers)


def multi_chain_comparison(file_path):
    """Führt Multi-Chain-Vergleiche mit einem LLM durch."""
    print(f"[Pipeline] Multi Chain Comparison wird ausgeführt für: {file_path}")
    # Beispielhafte Implementierung kann Multi-Temperaturen-Prozesse starten


def add_improve_docstrings(file_path):
    """Fügt Docstrings hinzu oder verbessert bestehende."""
    print(f"[Pipeline] Docstrings werden hinzugefügt/verbessert für: {file_path}")
    process_file_for_docstrings(file_path)


def run_sourcery(file_path):
    """Optimiert den Code mit Sourcery."""
    print(f"[Pipeline] Sourcery wird ausgeführt für: {file_path}")
    if not run_sourcery_fix(file_path):
        print(f"[Pipeline] Sourcery konnte keine Verbesserungen für {file_path} durchführen.")
    print(f"[Pipeline] Sourcery wurde erfolgreich ausgeführt für: {file_path}")


def custom_prompt(file_path):
    """Führt eine benutzerdefinierte Aktion mit einem LLM durch."""
    print(f"Custom Prompt wird für {file_path} durchgeführt.")
    # Integration eines generativen Modells für benutzerdefinierte Prompts


def run_type_annotation_updater(file_path):
    """Fügt Typannotationen hinzu oder aktualisiert diese."""
    print(f"[Pipeline] Typannotationen werden aktualisiert für: {file_path}")
    annotation_process_file(file_path)


action_functions = {
    "Pylint": run_pylint,
    "SonarQube": run_sonarqube,
    "Black": run_black,
    "Isort": run_isort,
    "Move Imports": move_imports,
    "Refactor": run_refactor,
    "Multi Chain Comparison": multi_chain_comparison,
    "Add/Improve Docstrings": add_improve_docstrings,
    "Sourcery": run_sourcery,
    "Custom Prompt": custom_prompt,
    "Type Annotation Updater": run_type_annotation_updater
}
