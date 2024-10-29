"""
This script analyzes Python files in a given directory to extract and visualize 
    dependencies between them. 
It identifies both external library dependencies and internal project file 
    dependencies.

Example usage:
    1. Extract dependencies from the 'Quizcraft' directory and save them 
        to 'dependencies.json'.
    2. Create and display a dependency graph from 'dependencies.json'.
"""

import ast
import os
import json
import networkx as nx
import matplotlib.pyplot as plt

def extract_dependencies_from_file(file_path, project_files):
    """Extract dependencies from a Python file, differentiating between libraries
        and project files."""
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    imports = {
        "libraries": set(),
        "project_files": set()
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split('.')[0]
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

    return {
        "libraries": list(imports["libraries"]),
        "project_files": list(imports["project_files"])
    }

def extract_dependencies_from_directory(directory):
    """Extract dependencies from all Python files in a directory."""
    dependencies = {}
    project_files =set(file.split('.')[0] for file in os.listdir(directory) if file.endswith(".py"))
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_deps = extract_dependencies_from_file(file_path, project_files)
                dependencies[file] = file_deps
    return dependencies

def save_dependencies_to_json(dependencies, output_file):
    """Save extracted dependencies to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dependencies, f, indent=4)
    print(f"Dependencies saved in '{output_file}'.")

# Beispielaufruf
DIRECTORY_PATH = "./Quizcraft"
OUTPUT_FILE = "dependencies.json"
DEPENDENCIES = extract_dependencies_from_directory(DIRECTORY_PATH)
save_dependencies_to_json(DEPENDENCIES, OUTPUT_FILE)

def create_dependency_graph(dependencies_json):
    """Create and display a dependency graph from a JSON file of dependencies."""
    with open(dependencies_json, "r", encoding="utf-8") as f:
        dependencies = json.load(f)

    graph = nx.DiGraph()
    for file, deps in dependencies.items():
        graph.add_node(file)
        for dep_file in deps["project_files"]:
            dep_filename = f"{dep_file}.py"
            if dep_filename in dependencies:
                graph.add_edge(file, dep_filename)

    plt.figure(figsize=(12, 10))
    pos = nx.shell_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=500, width=0.8, font_size=8,
            node_color="skyblue", edge_color="gray", font_color="darkblue", font_weight="bold")
    plt.title("Dependency Graph of 'Quizcraft' Repository")
    plt.show()

create_dependency_graph(OUTPUT_FILE)
