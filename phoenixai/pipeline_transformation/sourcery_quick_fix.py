"""Module for automatically fixing Python code using Sourcery."""

import subprocess
import logging
import os
from typing import Optional


def run_sourcery_fix(file_path: str) -> bool:
    """Runs Sourcery to automatically fix the code in the specified file.

    Args:
        file_path (str): Path to the Python file to be fixed.

    Returns:
        bool: True if the process was successful, False otherwise."""
    if not os.path.exists(file_path):
        logging.error(f"Datei '{file_path}' existiert nicht.")
        return False
    command = ["sourcery", "review", "--fix", file_path]
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding="utf-8"
        )
        logging.info(f"Sourcery hat '{file_path}' erfolgreich korrigiert.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Sourcery konnte '{file_path}' nicht korrigieren.")
        logging.error(f"Fehlerausgabe: {e.stderr}")
        return False


def main():
    """Main function to run Sourcery fix on a given file."""
    file_path = "phoenixai\\transformation\\base_prompt_handling.py"
    if success := run_sourcery_fix(file_path):
        print(f"Sourcery hat '{file_path}' erfolgreich korrigiert.")
    else:
        print(f"Sourcery konnte '{file_path}' nicht korrigieren.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
