"""Module for running iterative pylint workflow."""

import os
from phoenixai.pipeline_transformation.pylint_workflow import iterative_process_with_pylint


def main():
    """Main function to run the iterative pylint workflow."""
    file_path = "C:\\Users\\Anwender\\PycharmProjects\\PhoenixAI\\phoenixai\\repo_management\\manage_legacy_repo.py"
    iterations = 3  # Anzahl der Durchläufe

    if not os.path.exists(file_path):
        print(f"Datei '{file_path}' nicht gefunden.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        code_content = f.read()

    print("[DEBUG] Beginne iterative_process_with_pylint...")
    iterative_process_with_pylint(file_path, code_content, iterations)
    print("[DEBUG] iterative_process_with_pylint abgeschlossen.")



if __name__ == "__main__":
    main()
