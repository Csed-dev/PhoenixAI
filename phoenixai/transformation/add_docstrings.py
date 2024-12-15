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
You are tasked with creating **only docstrings** for the provided Python code.
Do not execute or modify the code itself. Do not explain anything or provide additional commentary.

**Your task:**

1. **Create or update the module-level docstring** if it is missing or incomplete.
   - The module-level docstring must summarize the purpose of the file and provide any necessary contextual information.
   - It must always appear as the first statement in the file.

2. For each function, method, or class in the file, generate or improve their docstrings, ensuring they follow the **Google-style format** as outlined below.

---

### Google Docstring Guidelines:

#### **Module Docstrings**
- The module docstring summarizes the purpose of the file, including its contents and usage.
- This docstring must be at the top of the file, above any imports or code.

#### **Function & Method Docstrings**
- Describe the usage and behavior (not implementation details).
- Use the following structure:
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

#### Example:
```python
\"\"\"
This module provides utility functions for data processing.

The functions include:
- A function for reading data.
- A function for cleaning data.
- A function for visualizing data.
\"\"\"

def example_function(param1: str, param2: int) -> bool:
    \"\"\"
    Brief summary of the function.

    Args:
        param1 (str): Description of param1.
        param2 (int): Description of param2.

    Returns:
        bool: Description of the return value.

    Raises:
        ValueError: If a certain error condition occurs.
    \"\"\"
    pass

### Output Requirements:

1. Do **not** modify the code itself—focus only on creating or improving docstrings.
2. Insert the module-level docstring at the top of the file, followed by any existing imports or code.
3. Ensure all docstrings adhere to the Google-style format.
4. Respond **only** with the updated code and its docstrings, so that I can copy your entire output without any adaptations.

Here is the Python code:
{code_snippet}
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
            raise ValueError("[Docstring-Updater] Keine Antwort vom LLM erhalten.")
    except Exception as e:
        raise RuntimeError(f"[Docstring-Updater]  Fehler beim LLM-Aufruf: {e}")


def update_module_docstring(original_ast, llm_ast):
    """
    Aktualisiert den Modul-Docstring im AST, falls vorhanden, oder fügt ihn hinzu, falls keiner existiert.

    Args:
        original_ast (ast.Module): Der ursprüngliche AST des Codes.
        llm_ast (ast.Module): Der AST des vom LLM generierten Codes.
    """
    # Extrahiere den Modul-Docstring aus dem LLM-Output
    llm_module_docstring = None
    if (
        isinstance(llm_ast.body[0], ast.Expr)
        and isinstance(llm_ast.body[0].value, ast.Constant)
        and isinstance(llm_ast.body[0].value.value, str)
    ):
        llm_module_docstring = llm_ast.body[0].value.value  # Der neue Modul-Docstring
        print("[Debug] Neuer Modul-Docstring aus LLM:", llm_module_docstring)

    if llm_module_docstring:
        # Überprüfen, ob der Originalcode bereits einen Modul-Docstring hat
        if (
            isinstance(original_ast.body[0], ast.Expr)
            and isinstance(original_ast.body[0].value, ast.Constant)
            and isinstance(original_ast.body[0].value.value, str)
        ):
            print("[Debug] Originaler Modul-Docstring wird ersetzt.")
            original_ast.body[0] = ast.Expr(value=ast.Constant(value=llm_module_docstring))
        else:
            print("[Debug] Kein Modul-Docstring vorhanden. Neuer wird hinzugefügt.")
            original_ast.body.insert(0, ast.Expr(value=ast.Constant(value=llm_module_docstring)))




def update_function_and_class_docstrings(original_ast, llm_ast):
    """
    Aktualisiert die Docstrings von Funktionen und Klassen im AST.
    """
    for node in original_ast.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            for llm_node in llm_ast.body:
                if isinstance(llm_node, (ast.FunctionDef, ast.ClassDef)) and node.name == llm_node.name:
                    new_docstring = ast.get_docstring(llm_node)
                    if new_docstring:
                        node.body = [
                            ast.Expr(value=ast.Constant(value=new_docstring))  # Füge den neuen Docstring ein
                        ] + [
                            n for n in node.body if not isinstance(n, ast.Expr) or not (
                                isinstance(n.value, ast.Constant)
                                and isinstance(n.value.value, str)
                            )
                        ]


def insert_docstrings_to_code(original_code, llm_response):
    """
    Fügt die generierten Docstrings in den Originalcode ein oder ersetzt bestehende Docstrings.
    """
    try:
        original_ast = ast.parse(original_code)
        try:
            llm_ast = ast.parse(llm_response)
        except SyntaxError as parse_error:
            raise RuntimeError(f"[Docstring-Updater] Ungültiger LLM-Code: {llm_response}") from parse_error

        # Aktualisiere Modul-Docstring
        update_module_docstring(original_ast, llm_ast)
        
        # Aktualisiere Funktions- und Klassendocstrings
        update_function_and_class_docstrings(original_ast, llm_ast)

        return astor.to_source(original_ast)
    except Exception as e:
        raise RuntimeError(f"[Docstring-Updater] Fehler beim Einfügen der Docstrings: {e}")


def save_code_with_docstrings(file_path, updated_code):
    """Speichert den Code mit den neuen Docstrings."""
    output_file = file_path.replace(".py", "_docstrings.py")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(updated_code)
    print(f"[Docstring-Updater] Der aktualisierte Code wurde gespeichert: {output_file}")


def process_file_for_docstrings(file_path, max_retries=5):
    """Kompletter Prozess zur Generierung und Einfügung von Docstrings mit Wiederholungslogik."""
    original_code = extract_code_for_llm(file_path)
    prompt = generate_docstring_prompt(original_code)
    
    last_llm_response = None  # Speichert die letzte LLM-Antwort für Debugging
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Docstring-Updater] Versuch {attempt}: LLM wird aufgerufen...")
            llm_response = call_llm_for_docstrings(prompt)
            print(llm_response) # enfernen
            last_llm_response = llm_response  # Speichere den aktuellen LLM-Output
            trimmed_code = trim_code(llm_response)
            
            # Teste, ob der LLM-Code gültig ist
            print("[Docstring-Updater] [Debug] Überprüfe die Gültigkeit des zurückgegebenen Codes...")
            ast.parse(trimmed_code)  # Validiert, ob der Code parsebar ist
            
            # Wenn kein Fehler auftritt, führe den Einfügeprozess aus
            updated_code = insert_docstrings_to_code(original_code, trimmed_code)
            save_code_with_docstrings(file_path, updated_code)
            break
        except SyntaxError as e:
            print(f"[Docstring-Updater] [Fehler] Syntaxfehler im LLM-Code bei Versuch {attempt}: {e}")
            print(f"[Docstring-Updater] [Debug] Ungültiger LLM-Code:\n{last_llm_response}")
        except Exception as e:
            print(f"[Docstring-Updater] [Fehler] Unerwarteter Fehler bei Versuch {attempt}: {e}")
        
        if attempt == max_retries:
            # Letzten LLM-Output speichern für Debugging
            with open("[Docstring-Updater]  last_failed_llm_response.txt", "w", encoding="utf-8") as f:
                f.write(last_llm_response or "[Docstring-Updater]  Keine gültige Antwort erhalten.")
            raise RuntimeError("[Docstring-Updater]  Fehler: Maximale Anzahl an LLM-Aufrufen erreicht, ohne gültige Docstrings zu erhalten.")



if __name__ == "__main__":
    file_to_process = "phoenixai\\transformation\\base_prompt_handling.py"
    process_file_for_docstrings(file_to_process)
