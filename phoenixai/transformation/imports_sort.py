import ast
import astor

from base_prompt_handling import read_file, run_black_and_isort, save_code_to_file

def collect_imports_and_format(file_path):
    """
    Bringt alle Import-Anweisungen einer Datei nach oben, speichert den aktualisierten Code
    in einer neuen Datei und führt anschließend isort und Black darauf aus.

    :param file_path: Pfad zur Python-Datei.
    """
    original_code = read_file(file_path)

    # AST-Parsing
    tree = ast.parse(original_code)
    imports = []
    other_code_lines = []

    # Sammle alle Import-Anweisungen und den restlichen Code
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(astor.to_source(node).strip())
        else:
            other_code_lines.append(astor.to_source(node).strip())

    unique_imports = sorted(set(imports)) # Entferne Duplikate bei Importen
    updated_code = "\n".join(unique_imports) + "\n\n" + "\n".join(other_code_lines)
    save_code_to_file(file_path, updated_code)
    print(f"[Sort-Imports] Import-Anweisungen wurden nach oben verschoben und die Datei wurde gespeichert: {file_path}")
    run_black_and_isort(file_path)



if __name__ == "__main__":

    collect_imports_and_format("C:\\Users\\Anwender\\PycharmProjects\\PhoenixAI\\phoenixai\\transformation\\base_prompt_handling.py")
