import ast
import os
import subprocess
from pathlib import Path
import astor




# Beispielaufruf
if __name__ == "__main__":
    collect_and_fix_imports("phoenixai\\transformation\\test_imports.py")

import ast
import astor
from pathlib import Path
import subprocess

def extract_imports(tree):
    imports = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(astor.to_source(node).strip())
    return imports

def extract_code_without_imports(tree):
    code_lines = []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            code_lines.append(astor.to_source(node).strip())
    return code_lines

def format_code(imports, code_lines):
    unique_imports = sorted(set(imports))
    return '\n'.join(unique_imports) + '\n\n' + '\n'.join(code_lines)

def write_updated_code_to_file(file_path, updated_code):
    new_file_path = Path(file_path).with_name(f'{Path(file_path).stem}_fixed_imports.py')
    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write(updated_code)
    return new_file_path

def run_isort(file_path):
    try:
        subprocess.run(['isort', str(file_path)], check=True)
        print(f'isort erfolgreich auf {file_path} angewendet.')
    except subprocess.CalledProcessError as e:
        print(f'Fehler beim Ausführen von isort: {e}')

def collect_and_fix_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()
    tree = ast.parse(original_code)
    imports = extract_imports(tree)
    code_lines = extract_code_without_imports(tree)
    updated_code = format_code(imports, code_lines)
    new_file_path = write_updated_code_to_file(file_path, updated_code)
    print(f'Import-Anweisungen wurden angepasst und die Datei wurde gespeichert: {new_file_path}')
    run_isort(new_file_path)