import ast
import os
import subprocess
from pathlib import Path
import astor


def collect_and_fix_imports(file_path):
    """
    Sammelt alle Import-Anweisungen aus einer Python-Datei, sortiert und bereinigt sie,
    und speichert den bereinigten Code in einer neuen Datei. Führt anschließend isort auf der neuen Datei aus.

    :param file_path: Pfad zur Python-Datei.
    """
    # Datei einlesen
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    # AST-Parsing
    tree = ast.parse(original_code)
    imports = []
    new_code_lines = []

    # Sammle Import-Anweisungen und den restlichen Code
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(astor.to_source(node).strip())
        else:
            new_code_lines.append(astor.to_source(node).strip())

    # Entferne Duplikate und sortiere
    unique_imports = sorted(set(imports))

    # Erstelle den neuen Code
    updated_code = "\n".join(unique_imports) + "\n\n" + "\n".join(new_code_lines)

    # Neue Datei erstellen und speichern
    new_file_path = Path(file_path).with_name(f"{Path(file_path).stem}_fixed_imports.py")
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(updated_code)

    print(f"Import-Anweisungen wurden angepasst und die Datei wurde gespeichert: {new_file_path}")

    # Führe isort auf der neuen Datei aus
    try:
        subprocess.run(["isort", str(new_file_path)], check=True)
        print(f"isort erfolgreich auf {new_file_path} angewendet.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von isort: {e}")


# Beispielaufruf
if __name__ == "__main__":
    collect_and_fix_imports("phoenixai\\transformation\\test_imports.py")
