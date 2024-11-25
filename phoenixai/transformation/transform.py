import os
from pylint_workflow import process_file_with_pylint, iterative_process_with_pylint

def main():
    file_path = "phoenixai/repo_management/manage_legacy_repo.py"
    iterations = 3  # Anzahl der Durchläufe

    if not os.path.exists(file_path):
        print(f"Datei '{file_path}' nicht gefunden.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        code_content = f.read()

    # Iterativer Workflow mit Pylint und LLM
    final_result = iterative_process_with_pylint(file_path, code_content, iterations)

    if final_result:
        print("Finaler verbesserter Code:")
        print(final_result)
    else:
        print("Kein finaler Output erhalten.")

if __name__ == "__main__":
    main()
