import ast
import os
import astor
import google.generativeai as genai
from dotenv import load_dotenv

from base_prompt_handling import trim_code

# LLM-Konfiguration
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY nicht gesetzt. Bitte setzen Sie die Umgebungsvariable.")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_code_for_llm(file_path):
    """Liest den Python-Code aus einer Datei."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

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

def call_llm_for_annotations(prompt):
    """Ruft das LLM auf, um Typannotationen zu generieren."""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.7),
        )
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            raise ValueError("Keine Antwort vom LLM erhalten.")
    except Exception as e:
        raise RuntimeError(f"Fehler beim LLM-Aufruf: {e}")

def insert_type_annotations(original_code, llm_response):
    """
    Fügt die generierten Typannotationen in den Originalcode ein oder ersetzt bestehende Annotationen.

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
                # Suche das passende LLM-Knoten
                for llm_node in llm_ast.body:
                    if isinstance(llm_node, ast.FunctionDef) and node.name == llm_node.name:
                        # Update argument annotations
                        for original_arg, llm_arg in zip(node.args.args, llm_node.args.args):
                            original_arg.annotation = llm_arg.annotation

                        # Update return type annotation
                        node.returns = llm_node.returns
        
        return astor.to_source(original_ast)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Einfügen der Typannotationen: {e}")

def save_code_with_annotations(file_path, updated_code):
    """Speichert den Code mit den neuen Typannotationen."""
    output_file = file_path.replace(".py", "_typed.py")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(updated_code)
    print(f"Der aktualisierte Code wurde gespeichert: {output_file}")

def annotation_process_file(file_path):
    """Kompletter Prozess zur Generierung und Einfügung von Typannotationen."""
    original_code = extract_code_for_llm(file_path)
    prompt = generate_type_annotation_prompt(original_code)
    llm_response = call_llm_for_annotations(prompt)
    trimmed_llm_code = trim_code(llm_response)
    updated_code = insert_type_annotations(original_code, trimmed_llm_code)
    save_code_with_annotations(file_path, updated_code)