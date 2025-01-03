"""Modul zur automatischen Korrektur von Python-Code mit Sourcery."""

import subprocess
import logging
import os
from typing import Optional


def run_sourcery_fix(file_path: str) -> bool:
    """
    Führt Sourcery aus, um den Code in der angegebenen Datei automatisch zu korrigieren.

    :param file_path: Pfad zur zu korrigierenden Python-Datei.
    :param sourcery_token: Dein Sourcery-API-Token, falls erforderlich.
    :return: True, wenn der Prozess erfolgreich war, sonst False.
    """
    if not os.path.exists(file_path):
        logging.error(f"Datei '{file_path}' existiert nicht.")
        return False

    command = ["sourcery", "review", "--fix", file_path]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        logging.info(f"Sourcery hat '{file_path}' erfolgreich korrigiert.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Sourcery konnte '{file_path}' nicht korrigieren.")
        logging.error(f"Fehlerausgabe: {e.stderr}")
        return False


def main():
    """Hauptfunktion, um Sourcery-Fix auf eine gegebene Datei auszuführen."""
    file_path = "phoenixai\\transformation\\base_prompt_handling.py"

    if success := run_sourcery_fix(file_path):
        print(f"Sourcery hat '{file_path}' erfolgreich korrigiert.")
    else:
        print(f"Sourcery konnte '{file_path}' nicht korrigieren.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
