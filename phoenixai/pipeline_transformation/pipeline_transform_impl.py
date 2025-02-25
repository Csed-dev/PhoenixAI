# pipeline_transform_impl.py
import os
from phoenixai.pipeline_transformation.refactor import (
    save_selected_functions,
    process_single_function, select_functions_to_refactor,
)
from phoenixai.pipeline_transformation.add_docstrings import process_file_for_docstrings
from phoenixai.utils.base_prompt_handling import (
    apply_isort_to_file,
    format_file_with_black,
)
from phoenixai.pipeline_transformation.imports_sort import collect_imports_and_format
from phoenixai.pipeline_transformation.pylint_workflow import (
    iterative_process_with_pylint,
)
from phoenixai.pipeline_transformation.sourcery_quick_fix import run_sourcery_fix
from phoenixai.pipeline_transformation.typ_annotation_updater import (
    annotation_process_file,
)


def run_refactor(file_path):
    print("[DEBUG] run_refactor gestartet", flush=True)
    print(f"[Transform] Refactor für {file_path}", flush=True)
    selected_functions = select_functions_to_refactor(file_path)
    print("[DEBUG] Nach Dialog, ausgewählte Funktionen:", selected_functions, flush=True)
    if not selected_functions:
        print("[DEBUG] Keine Funktionen ausgewählt.", flush=True)
        return
    print("[DEBUG] Refactor beginnt", flush=True)
    temp_file_path = save_selected_functions(selected_functions)
    print(f"[DEBUG] Temp-Datei erstellt: {temp_file_path}", flush=True)
    for func_name in selected_functions:
        print(f"[DEBUG] Bearbeite Funktion: {func_name}", flush=True)
        process_single_function(file_path, func_name)
        print(f"[DEBUG] Prozess für Funktion {func_name} beendet", flush=True)
    os.remove(temp_file_path)
    print(f"[DEBUG] Temporäre Datei {temp_file_path} gelöscht.", flush=True)


def run_add_docstrings(file_path):
    print(f"[Transform] Docstrings für {file_path}")
    process_file_for_docstrings(file_path)


def run_type_annotation_updater(file_path):
    print(f"[Transform] Type Annotation für {file_path}")
    annotation_process_file(file_path)


def run_move_imports(file_path):
    print(f"[Transform] Imports sortieren für {file_path}")
    collect_imports_and_format(file_path)


def run_isort(file_path):
    apply_isort_to_file(file_path)


def run_black(file_path):
    format_file_with_black(file_path)


def run_pylint(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code_content = f.read()
    iterative_process_with_pylint(file_path, code_content, 1)


def run_sourcery(file_path):
    if not run_sourcery_fix(file_path):
        print("[Transform] Keine Verbesserungen mit Sourcery.")
    else:
        print("[Transform] Sourcery erfolgreich.")


def run_custom_prompt(file_path):
    print(f"[Transform] Custom Prompt für {file_path}")


# Dictionary aller Transform-Aktionen
transform_actions = {
    "Refactor": run_refactor,
    "Add/Improve Docstrings": run_add_docstrings,
    "Type Annotation Updater": run_type_annotation_updater,
    "Move Imports": run_move_imports,
    "Isort": run_isort,
    "Black": run_black,
    "Pylint": run_pylint,
    "Sourcery": run_sourcery,
}
