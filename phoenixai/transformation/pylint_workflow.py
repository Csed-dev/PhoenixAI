"""Module for iterative code improvement using LLM and Pylint."""

import ast
import subprocess
import logging
import sqlite3
import re
import os
from typing import List, Tuple, Dict
from base_prompt_handling import (
    generate_initial_prompt,
    call_llm,
    trim_code,
    save_code_to_file,
    extract_code_from_response,
)
from multi_chain_comparison import MultiChainComparison


def setup_multichain_comparison(temperatures: List[float]) -> MultiChainComparison:
    """Creates and configures the MultiChainComparison instance."""
    multi_chain = MultiChainComparison("", temperatures, "pylint")
    multi_chain.register_comparison_function("pylint", compare_pylint_results)
    return multi_chain


def analyze_with_pylint(file_path: str) -> Tuple[List[Dict[str, str]], str]:
    """Runs Pylint and generates the formatted error description."""
    pylint_output = run_pylint(file_path)
    errors = extract_error_codes_and_messages(pylint_output)
    error_descriptions = build_error_report(errors)
    formatted_errors = format_errors_for_prompt(error_descriptions)
    return errors, formatted_errors


def should_stop_iteration(previous_error_count: int, current_error_count: int) -> bool:
    """Checks if the iteration should be stopped based on error count."""
    if previous_error_count is not None and current_error_count >= previous_error_count:
        logging.warning(
            "No improvement detected or code got worse. Stopping iterations."
        )
        return True
    return False


def run_multichain_for_code_improvement(
    multi_chain: MultiChainComparison, code_content: str, formatted_errors: str
) -> str:
    """Runs MultiChainComparison to find the best result based on LLM responses."""
    prompt = create_full_prompt(code_content, formatted_errors)
    multi_chain.prompt = prompt
    return multi_chain.run(call_llm)


def process_and_validate_code(
    improved_code: str, file_path: str, iteration: int
) -> str:
    """Processes and validates the code generated by the LLM."""
    trimmed_code = extract_code_from_response(improved_code)
    formatted_code = format_code_with_black(trimmed_code)

    if is_valid_python_code(formatted_code):
        save_code_to_file(file_path, formatted_code, iteration)
        logging.info("Improved code saved in iteration %d.", iteration)
        return formatted_code

    logging.error("The code returned by the LLM contains syntax errors.")
    return ""


def update_file_path(file_path: str, iteration: int) -> str:
    """Updates the file path for the next iteration."""
    base_name, ext = os.path.splitext(file_path)
    return f"{base_name}_improved_{iteration}{ext}"


def compare_pylint_results(
    results: List[str], temperatures: List[float]
) -> Tuple[int, str]:
    """Compares results based on the Pylint score and selects the best one."""
    scores = []
    for idx, result in enumerate(results):
        temp = temperatures[idx]
        cleaned_code = trim_code(result)
        temp_file = save_to_temp_file(cleaned_code, idx)
        try:
            pylint_output = run_pylint(temp_file)
            score = extract_pylint_score(pylint_output)
            scores.append((score, idx, cleaned_code))
            print(
                "[Pylint-Workflow] Temperature %.1f: Pylint-Score %.1f/10"
                % (temp, score)
            )
        finally:
            remove_temp_file(temp_file)
    return select_best_result(scores)


def save_to_temp_file(cleaned_code: str, idx: int) -> str:
    """Saves the cleaned code to a temporary file."""
    temp_file = f"temp_file_{idx}.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(cleaned_code)
    return temp_file


def remove_temp_file(temp_file: str):
    """Removes the temporary file if it exists."""
    try:
        os.remove(temp_file)
    except OSError as e:
        logging.warning("Temp file could not be deleted: %s", e)


def select_best_result(scores: List[Tuple[float, int, str]]) -> Tuple[int, str]:
    """Selects the result with the highest Pylint score."""
    best_result = max(scores, key=lambda x: x[0])
    return best_result[1], best_result[2]


def extract_pylint_score(pylint_output: str) -> float:
    """Extracts the Pylint score from the output."""
    try:
        if match := re.search(
            r"Your code has been rated at (-?\d+\.\d+)/10", pylint_output
        ):
            return float(match[1])

        logging.warning("Pylint score could not be extracted. Using default value 0.0.")
        return 0.0
    except Exception as e:
        logging.error("Error extracting Pylint score: %s", e)
        return 0.0


def format_code_with_black(code):
    """Formats the code with Black."""
    temp_file = "temp_code.py"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(code)
    subprocess.run(["black", temp_file], check=True)
    with open(temp_file, "r", encoding="utf-8") as f:
        formatted_code = f.read()
    os.remove(temp_file)
    return formatted_code


def is_valid_python_code(code_str):
    """Checks if the code is valid Python code."""
    try:
        ast.parse(code_str)
        return True
    except SyntaxError as e:
        logging.error("Syntax error in code: %s", e)
        return False


def run_pylint(file_path):
    """Runs Pylint and returns the raw output."""
    result = subprocess.run(
        ["pylint", file_path],
        capture_output=True,
        text=True,
    )
    return result.stdout


def extract_error_codes_and_messages(pylint_output):
    """Extracts error codes and messages from Pylint output."""
    matches = re.findall(r": ([A-Z]\d{4}): (.+?)(?:\n|$)", pylint_output)
    return [{"error_code": match[0], "message_emitted": match[1]} for match in matches]


def fetch_error_description_from_db(error_code):
    """Fetches error description from the database."""
    db_path = "phoenixai/database/code_quality_tests.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT description FROM pylint_test WHERE error_code = ?""", (error_code,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def build_error_report(errors):
    """Combines error ID, message, and description into a list."""
    descriptions = []
    for error in errors:
        description = fetch_error_description_from_db(error["error_code"])
        description = description or "Description not found"
        descriptions.append(
            f"- {error['error_code']} ({error['message_emitted']}): {description}"
        )
    return descriptions


def format_errors_for_prompt(error_descriptions):
    """Formats error details for the LLM prompt."""
    return "\n".join(error_descriptions)


def create_full_prompt(code_content, formatted_errors):
    """Creates the full prompt for the LLM."""
    return generate_initial_prompt(code_content) + formatted_errors


def iterative_process_with_pylint(file_path, code_content, iterations):
    """Iteratively runs the workflow based on the given number of iterations."""
    logging.basicConfig(level=logging.INFO)
    temperatures = [0.2, 0.4, 0.6]
    multi_chain = setup_multichain_comparison(temperatures)
    previous_error_count = None
    for i in range(1, iterations + 1):
        logging.info("--- Iteration %d/%d started ---", i, iterations)
        errors, formatted_errors = analyze_with_pylint(file_path)
        if not errors:
            logging.info("No error codes found. Workflow finished.")
            break
        current_error_count = len(errors)
        if should_stop_iteration(previous_error_count, current_error_count):
            break
        previous_error_count = current_error_count
        improved_code = run_multichain_for_code_improvement(
            multi_chain, code_content, formatted_errors
        )
        if not improved_code.strip():
            logging.error("No valid response from LLM in iteration %d. Abort.", i)
            break
        if formatted_code := process_and_validate_code(
            improved_code, file_path, i
        ):
            code_content = formatted_code
            file_path = update_file_path(file_path, i)
        else:
            break
    logging.info("Iterative workflow finished.")
