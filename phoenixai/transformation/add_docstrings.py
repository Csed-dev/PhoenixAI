import ast
import os
import re

import astor
import google.generativeai as genai
from dotenv import load_dotenv

from base_prompt_handling import trim_code

# LLM-Konfiguration
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY nicht gesetzt. Bitte setzen Sie die Umgebungsvariable."
    )

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_code_for_llm(file_path):
    """Liest den Python-Code aus einer Datei."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_docstring_prompt(code_snippet):
    """
    Generates a prompt for the LLM to create docstrings for a given Python code snippet.

    Args:
        code_snippet (str): The Python code snippet for which to generate docstrings.

    Returns:
        str: The formatted prompt for the LLM.
    """
    return f"""
Here is the Python code: {code_snippet}

**Output the code with the inserted or updated docstrings, maintaining proper formatting and indentation.**

Your task is to generate and insert **docstrings** following the specified Google format and style guidelines.

### Google Docstring Guidelines:

#### **General Format**
1. Use triple double quotes for all docstrings.
2. Start with a one-line summary ending in a period, question mark, or exclamation point.
3. If additional details are necessary, add them after a blank line.

#### **Module Docstrings**
- Include a top-level docstring summarizing the module’s contents and usage.
- For test modules, provide docstrings only if they add meaningful information.

#### **Function & Method Docstrings**
- Mandatory for public APIs or any complex/non-obvious functions.
- Describe usage and behavior (not implementation details).
- Use consistent style: either descriptive (e.g., "Fetches rows…") or imperative (e.g., "Fetch rows…").
- Document arguments, return values, and exceptions with structured sections:
  - **Args:** List parameters with descriptions and types (if not annotated).
  - **Returns:** Describe the return value and type. For multiple values, list as elements of a returned tuple.
  - **Yields:** For generators, describe the yielded values.
  - **Raises:** List exceptions and their conditions.

#### **Class Docstrings**
- Begin with a single-line summary of the class's purpose.
- Add extended details after a blank line.
- **Attributes:** Document public attributes in the format used for function args.

#### **Inline Comments**
- Use sparingly to clarify non-obvious logic.
- Explain intent or reasoning, not literal code behavior.
- Begin inline comments with `#`, two spaces after the code.

### Your Task:
1. Do **not** modify the code itself—focus only on generating or improving docstrings.
2. Insert docstrings directly into the relevant sections of the provided code.
3. Ensure the docstrings adhere to the Google-style format.
"""



def call_llm_for_docstrings(prompt):
    """Ruft das LLM auf, um Docstrings zu generieren."""
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


def insert_docstrings_to_code(original_code, llm_response):
    """
    Fügt die generierten Docstrings in den Originalcode ein oder ersetzt bestehende Docstrings.
    """
    try:
        original_ast = ast.parse(original_code)
        llm_ast = ast.parse(llm_response)

        # Iteriere über alle Knoten im Original-AST
        for node in original_ast.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Suche den passenden Knoten im LLM-AST
                for llm_node in llm_ast.body:
                    if (
                        isinstance(llm_node, (ast.FunctionDef, ast.ClassDef))
                        and node.name == llm_node.name
                    ):
                        # Extrahiere den neuen Docstring aus dem LLM-Knoten
                        new_docstring = ast.get_docstring(llm_node)
                        if new_docstring:
                            # Ersetze den bestehenden Docstring (falls vorhanden)
                            node.body = [
                                ast.Expr(value=ast.Constant(value=new_docstring))  # Verwendung von ast.Constant
                            ] + [
                                n
                                for n in node.body
                                if not isinstance(n, ast.Expr) or not (
                                    isinstance(n.value, ast.Constant)
                                    and isinstance(n.value.value, str)
                                )
                            ]
        return astor.to_source(original_ast)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Einfügen der Docstrings: {e}")




def save_code_with_docstrings(file_path, updated_code):
    """Speichert den Code mit den neuen Docstrings."""
    output_file = file_path.replace(".py", "_docstrings.py")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(updated_code)
    print(f"Der aktualisierte Code wurde gespeichert: {output_file}")


def process_file_for_docstrings(file_path):
    """Kompletter Prozess zur Generierung und Einfügung von Docstrings."""
    original_code = extract_code_for_llm(file_path)
    prompt = generate_docstring_prompt(original_code)
    llm_response = call_llm_for_docstrings(prompt)
    trimmed_code = trim_code(llm_response)
    updated_code = insert_docstrings_to_code(original_code, trimmed_code)
    save_code_with_docstrings(file_path, updated_code)


if __name__ == "__main__":
    file_to_process = "phoenixai\\transformation\\test_example_refactored.py"
    process_file_for_docstrings(file_to_process)
