import ast
import astor
import subprocess
import shutil

from phoenixai.utils.base_prompt_handling import (
    trim_code,
    read_file,
    save_code_to_file,
    call_llm,
    run_black_and_isort,
)

def generate_type_annotation_prompt(code_snippet):
    """
    Generates a prompt for the LLM to create or update type annotations for the given Python code snippet.

    Args:
        code_snippet (str): The Python code snippet for which to generate type annotations.

    Returns:
        str: The formatted prompt for the LLM.
    """
    return f"""
Here is the Python code: {code_snippet}

**Output the code with added or updated type annotations, maintaining proper formatting and indentation.**

Your task is to generate and insert **type annotations** for all classes, methods, and functions in the given Python code.

### Guidelines for Type Annotations:
1. Use standard Python typing conventions (e.g., `from typing import Any, List, Dict`).
2. For arguments and return values without clear types, use `Any`.
3. Use `Self` for methods that return the instance of the same class.
4. Ensure all annotations are consistent with the function/method usage.
5. Do **not** modify the code logic—focus only on type annotations.

### Your Task:
1. Add missing type annotations for all arguments and return values.
2. Keep existing type annotations unchanged unless they are incorrect.
3. Ensure that the updated code adheres to PEP 484 (Type Hints) guidelines.
"""

def insert_type_annotations(original_code, llm_response):
    """
    Inserts the generated type annotations into the original code or replaces existing annotations.

    Args:
        original_code (str): The original Python code.
        llm_response (str): The LLM-generated code with type annotations.

    Returns:
        str: The updated Python code with type annotations.
    """
    try:
        original_ast = ast.parse(original_code)
        llm_ast = ast.parse(llm_response)

        for node in original_ast.body:
            if isinstance(node, ast.FunctionDef):
                # Find the matching function in the LLM response
                for llm_node in llm_ast.body:
                    if isinstance(llm_node, ast.FunctionDef) and node.name == llm_node.name:
                        # Update argument annotations
                        for orig_arg, llm_arg in zip(node.args.args, llm_node.args.args):
                            orig_arg.annotation = llm_arg.annotation
                        # Update return annotation
                        node.returns = llm_node.returns

        return astor.to_source(original_ast)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Einfügen der Typannotationen: {e}") from e

def add_missing_typing_imports(code: str) -> str:
    """
    Scans the code for type annotations and automatically inserts missing imports from the typing module.

    Args:
        code (str): The Python code to process.

    Returns:
        str: The updated Python code with necessary typing imports.
    """
    required_types = {"Any", "List", "Dict", "Optional", "Union", "Tuple", "Set", "Self"}
    found_types = set()

    class TypeAnnotationVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            for arg in node.args.args:
                if arg.annotation:
                    self.process_annotation(arg.annotation)
            if node.returns:
                self.process_annotation(node.returns)
            self.generic_visit(node)

        def visit_AnnAssign(self, node):
            if node.annotation:
                self.process_annotation(node.annotation)
            self.generic_visit(node)

        def process_annotation(self, node):
            if isinstance(node, ast.Name):
                if node.id in required_types:
                    found_types.add(node.id)
            elif isinstance(node, ast.Subscript):
                self.process_annotation(node.value)
                self.process_annotation(node.slice)
            elif isinstance(node, ast.Tuple):
                for elt in node.elts:
                    self.process_annotation(elt)
            elif isinstance(node, ast.Attribute):
                # Skip attributes; assume proper qualified names are used
                pass
            elif isinstance(node, ast.Call):
                for arg in node.args:
                    self.process_annotation(arg)

    try:
        tree = ast.parse(code)
        visitor = TypeAnnotationVisitor()
        visitor.visit(tree)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Parsen des Codes: {e}") from e

    # Check for existing typing imports
    existing_imports = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "typing":
            for alias in node.names:
                existing_imports.add(alias.name)

    missing_imports = found_types - existing_imports
    if missing_imports:
        import_line = f"from typing import {', '.join(sorted(missing_imports))}\n"
        lines = code.splitlines()
        insert_pos = 0
        # If there is a module docstring, insert after it
        if lines and lines[0].startswith('"""'):
            for i in range(1, len(lines)):
                if lines[i].strip().endswith('"""'):
                    insert_pos = i + 1
                    break
        lines.insert(insert_pos, import_line)
        code = "\n".join(lines)
    return code

def annotation_process_file(file_path):
    """Complete process for generating and inserting type annotations, auto-adding necessary typing imports,
    and then applying isort.

    Args:
        file_path (str): The path to the file to be processed.
    """
    original_code = read_file(file_path)
    prompt = generate_type_annotation_prompt(original_code)
    llm_response = call_llm(prompt)
    trimmed_llm_code = trim_code(llm_response)
    updated_code = insert_type_annotations(original_code, trimmed_llm_code)
    updated_code = add_missing_typing_imports(updated_code)
    save_code_to_file(file_path, updated_code)
    run_black_and_isort(file_path)
