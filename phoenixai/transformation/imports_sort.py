import ast
import subprocess
from pathlib import Path
import astor


def collect_imports_and_format(file_path):
    """
    Bringt alle Import-Anweisungen einer Datei nach oben, speichert den aktualisierten Code
    in einer neuen Datei und führt anschließend isort und Black darauf aus.

    :param file_path: Pfad zur Python-Datei.
    """
    # Datei einlesen
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

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

    # Entferne Duplikate bei Importen
    unique_imports = sorted(set(imports))

    # Erstelle den neuen Code mit allen Importen oben
    updated_code = "\n".join(unique_imports) + "\n\n" + "\n".join(other_code_lines)

    # Neue Datei erstellen und speichern
    new_file_path = Path(file_path).with_name(f"{Path(file_path).stem}_fixed_imports.py")
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(updated_code)

    print(f"Import-Anweisungen wurden nach oben verschoben und die Datei wurde gespeichert: {new_file_path}")

    # isort und Black auf die neue Datei anwenden
    try:
        subprocess.run(["isort", str(new_file_path)], check=True)
        print(f"isort erfolgreich auf {new_file_path} angewendet.")
        subprocess.run(["black", str(new_file_path)], check=True)
        print(f"Black erfolgreich auf {new_file_path} angewendet.")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Formatieren mit isort oder Black: {e}")


# Beispielaufruf
if __name__ == "__main__":
    # Dateipfad angeben
    collect_imports_and_format("phoenixai\\transformation\\test_imports.py")
