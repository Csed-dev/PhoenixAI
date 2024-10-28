import ast
import os
import json
import networkx as nx
import matplotlib.pyplot as plt

def extract_dependencies_from_file(file_path, project_files):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
    
    # Sets für Libraries und Projektdateien
    imports = {
        "libraries": set(),
        "project_files": set()
    }

    # Durchlaufe alle 'import' und 'from ... import' Statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
                # Prüfe, ob das Modul eine Projektdatei ist oder eine externe Bibliothek
                if module_name in project_files:
                    imports["project_files"].add(module_name)
                else:
                    imports["libraries"].add(module_name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module.split('.')[0] if node.module else ""
            if module_name in project_files:
                imports["project_files"].add(module_name)
            else:
                imports["libraries"].add(module_name)
    
    # Liste zurückgeben
    return {
        "libraries": list(imports["libraries"]),
        "project_files": list(imports["project_files"])
    }

def extract_dependencies_from_directory(directory):
    dependencies = {}
    project_files = set(file.split('.')[0] for file in os.listdir(directory) if file.endswith(".py"))  # Namen ohne .py
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_deps = extract_dependencies_from_file(file_path, project_files)
                dependencies[file] = file_deps
    return dependencies

def save_dependencies_to_json(dependencies, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dependencies, f, indent=4)
    print(f"Abhängigkeiten wurden in '{output_file}' gespeichert.")

# Beispielaufruf
directory_path = "./Quizcraft"
output_file = "dependencies.json"
dependencies = extract_dependencies_from_directory(directory_path)
save_dependencies_to_json(dependencies, output_file)

# Graph aus den Projektdatei-Abhängigkeiten erstellen
def create_dependency_graph(dependencies_json):
    with open(dependencies_json, "r", encoding="utf-8") as f:
        dependencies = json.load(f)

    # Gerichteter Graph für Projektdateien
    G = nx.DiGraph()
    for file, deps in dependencies.items():
        G.add_node(file)
        for dep_file in deps["project_files"]:
            # Verbindung zwischen Dateien hinzufügen
            dep_filename = f"{dep_file}.py"  # Dateiendung anfügen
            if dep_filename in dependencies:
                G.add_edge(file, dep_filename)

    # Graph zeichnen
    plt.figure(figsize=(12, 10))
    pos = nx.shell_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=500, width=0.8, font_size=8, 
            node_color="skyblue", edge_color="gray", font_color="darkblue", font_weight="bold")
    plt.title("Dependency Graph des 'Quizcraft' Repository")
    plt.show()

# Erstelle den Graphen
create_dependency_graph(output_file)
