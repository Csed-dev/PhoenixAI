import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import logging

load_dotenv()

# LLM-Konfiguration
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY nicht gesetzt. Bitte setzen Sie die Umgebungsvariable.")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_initial_prompt(code_content):
    """Erstellt den Basisprompt für das LLM."""
    return f"""
Code:

{code_content}

Gib **nur** den verbesserten **reinen Code** zurück, ohne zusätzliche Erklärungen, 
Kommentare oder Markdown-Codeblöcke (wie ```python). Der Code sollte direkt 
ausgeführt werden können. Beachte, dass jede Datei einen Docstring benötigt.
Bitte verbessere den Python-Code, indem du die angegebenen Probleme behebst:

Zu behebende Probleme:
"""


# LLM-Aufruf
import google.generativeai as genai
import logging

def call_llm(prompt: str, temperature: float = 0.7) -> str:
    """
    Ruft das LLM (Gemini) mit einem bestimmten Prompt und einer spezifischen Temperatur auf.

    :param prompt: Der Eingabeprompt für das LLM.
    :param temperature: Die Kreativität des LLMs (Standard: 0.7).
    :return: Die generierte Ausgabe des LLMs.
    """
    try:
        # Anfrage senden
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                # candidate_count=1,  # Eine Ausgabe erzeugen
                temperature=temperature,
            )
        )

        # Generierte Ausgabe extrahieren
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            logging.error("Keine validen Ergebnisse vom LLM erhalten.")
            return ""

    except Exception as e:
        logging.error(f"Fehler beim Aufrufen des LLM: {e}")
        return ""

# Code trimmen
def strip_code_start(improved_code):
    """Entfernt Markdown-Markierungen"""
    lines = improved_code.splitlines()

    # Entferne ```python oder ``` nur am Anfang des Codes
    while lines and lines[0].strip() in ('```python', '```'):
        lines.pop(0)

    return '\n'.join(lines).strip()



def strip_code_end(improved_code):
    """Entfernt unerwünschten Text am Ende des Codes."""
    lines = improved_code.splitlines()

    # End-Index finden
    end_index = len(lines)
    for idx, line in enumerate(reversed(lines), 1):
        if line.strip() == "```":
            end_index = len(lines) - idx
        elif line.strip():
            break

    return '\n'.join(lines[:end_index]).strip()


def trim_code(improved_code):
    """Kombiniert die beiden Strip-Funktionen, um den Code vollständig zu trimmen."""
    code = strip_code_start(improved_code)
    code = strip_code_end(code)
    return code

def extract_code_from_response(response_text):
    """
    Extrahiert Code aus der LLM-Antwort, entfernt Codeblöcke und gibt den reinen Code zurück.
    """
    # falls der code nicht mit ```python beginnt, kann der step übersprüngen werden
    if not response_text.startswith("```python"):
        return response_text.strip()
    # Regex, um Code zwischen ```python und ``` zu finden
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", response_text, re.DOTALL)
    if code_blocks:
        # Wenn mehrere Codeblöcke vorhanden sind, diese kombinieren
        code = '\n'.join(code_blocks).strip()
    else:
        # Falls keine Codeblöcke gefunden wurden, gesamten Text zurückgeben
        code = response_text.strip()
    return code
    

# Code speichern
def save_code_to_file(file_path, improved_code, iteration):
    """Speichert den verbesserten Code in einer neuen Datei."""
    # Originaldateiname ohne bereits existierende Suffixe "_improved_X"
    base_name, ext = os.path.splitext(file_path)
    if "_improved_" in base_name:
        base_name = base_name.split("_improved_")[0]
    
    # Neuer Dateiname mit Iterationsnummer
    new_file_path = f"{base_name}_improved_{iteration}{ext}"
    
    # Datei schreiben
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(improved_code)
    
    return new_file_path

