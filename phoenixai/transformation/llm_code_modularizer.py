"""
modularize_code.py

Dieses Skript verwendet ein LLM, um gegebenen Python-Code zu analysieren und ihn modular aufzubauen. Ziel ist es, 
die Lesbarkeit, Wiederverwendbarkeit und Wartbarkeit des Codes zu verbessern.
"""

import logging
import os
from base_prompt_handling import call_llm, extract_code_from_response, save_code_to_file

logging.basicConfig(level=logging.INFO)


def generate_modular_prompt(code_content: str) -> str:
    """
    Erstellt einen Prompt für das LLM, um den gegebenen Code modular umzubauen.

    :param code_content: Der zu modularisierende Python-Code.
    :return: Der generierte LLM-Prompt.
    """
    return f"""
            Code:
            {code_content}

            Der folgende Python-Code sollte in wiederverwendbare Module umgewandelt werden. 
            Jede Funktion sollte, falls möglich
            nur eine Aufgabe erfüllen. Überprüfe den Code auf Wiederholungen und unnötige Komplexität.
            Ziel ist es, die Struktur zu verbessern, um die einzelnen Funktionen besser verstehen zu 
            können und um die Wartbarkeit zu erhöhen

            Hinweise:
            1. Jede Funktion oder Klasse sollte klar definierte Aufgaben haben.
            2. Überflüssige Wiederholungen im Code sollten vermieden werden.
            3. Am Anfang jeder Datei oder Klasse sollte ein beschreibender Docstring vorhanden sein.

            Gib **nur** den modularisierten Code zurück, ohne zusätzliche Erklärungen oder Kommentare außerhalb des Codes.
            """


def modularize_code(file_path: str) -> str:
    """
    Analysiert und modularisiert den Code in der angegebenen Datei.

    :param file_path: Der Pfad zur Python-Datei, die modularisiert werden soll.
    :return: Der modularisierte Code als String.
    """
    logging.info(f"Lade Datei: {file_path}")

    # Code aus der Datei lesen
    with open(file_path, "r", encoding="utf-8") as file:
        code_content = file.read()

    # Prompt für das LLM erstellen
    prompt = generate_modular_prompt(code_content)

    # LLM aufrufen
    logging.info("Rufe das LLM auf, um den Code zu modularisieren...")
    response = call_llm(prompt)

    # Extrahiere und bereinige den Code aus der LLM-Antwort
    modular_code = extract_code_from_response(response)

    if not modular_code.strip():
        logging.error("Das LLM hat keinen validen modularisierten Code zurückgegeben.")
        return ""

    return modular_code


def save_modularized_code(original_path: str, modular_code: str):
    """
    Speichert den modularisierten Code in einer neuen Datei.

    :param original_path: Der Pfad zur ursprünglichen Datei.
    :param modular_code: Der modularisierte Code.
    """
    new_file_path = save_code_to_file(original_path, modular_code, "modular")
    logging.info(f"Modularisierter Code gespeichert unter: {new_file_path}")


def main():
    """
    Hauptprogramm für die Code-Modularisierung.
    """
    file_path = "path/to/your/python_file.py"  # Zu modularisierende Datei

    if not os.path.exists(file_path):
        logging.error(f"Datei '{file_path}' nicht gefunden.")
        return

    if modular_code := modularize_code(file_path):
        save_modularized_code(file_path, modular_code)
    else:
        logging.error("Modularisierung fehlgeschlagen. Keine Änderungen vorgenommen.")


if __name__ == "__main__":
    main()
