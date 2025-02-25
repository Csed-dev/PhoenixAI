"""
This module processes SonarQube issues using a large language model (LLM) to suggest code improvements.

It analyzes SonarQube results, groups issues, generates prompts for an LLM, processes LLM responses, and saves improved code.
"""

import logging
from os.path import split
from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
print(sys.path)
from phoenixai.analysis.analyze import sonarqube_analysis
from phoenixai.utils.base_prompt_handling import (
    call_llm,
    generate_initial_prompt,
    save_code_to_file,
    trim_code,
)


def analyze_sonar_issues():
    """Performs a SonarQube analysis and returns the found issues.

    Returns:
        dict: A dictionary containing the issues, or None if no issues are found."""
    logging.info("Starte SonarQube-Analyse...")
    analysis_results = sonarqube_analysis()
    issues = analysis_results.get("issues", {})
    if not issues:
        logging.info("Keine SonarQube-Issues gefunden.")
        return None
    logging.info(f"Es wurden {len(issues)} Issues gefunden.")
    return issues


def group_issues(issues, group_size=10):
    """Splits the issues into groups of the specified size.

    Args:
        issues (dict): A dictionary containing all issues.
        group_size (int): The number of issues per group.

    Returns:
        list: A list of groups, where each group is a dictionary of issues."""
    logging.info(
        f"Teile {len(issues)} Issues in Gruppen mit jeweils {group_size} Issues."
    )
    issue_items = list(issues.items())
    return [
        dict(issue_items[i : i + group_size])
        for i in range(0, len(issue_items), group_size)
    ]


def generate_group_prompt(issues_group):
    """Creates a combined prompt for a group of issues.

    Args:
        issues_group (dict): A dictionary containing a group of issues.

    Returns:
        str: The generated prompt as a string."""
    logging.info(f"Erstelle Prompt für eine Gruppe mit {len(issues_group)} Issues.")
    prompt_parts = []
    for issue in issues_group["issues"]:
        prompt_parts.append(
            f"- {issue['message']} (SonarQube-Rule: {issue['rule']}) in Datei {issue['component']}."
        )
    prompt = f"{generate_initial_prompt('')}\n" + "\n".join(prompt_parts)
    return prompt


def process_group_with_llm(prompt, code_file_paths, iteration=1):
    """Sends the combined prompt to the LLM and saves the improved codes.

    Args:
        prompt (str): The generated prompt.
        code_file_paths (list): A list of affected files.
        iteration (int): The iteration number, used to save different versions.

    Returns:
        list: A list of paths to the improved files.

    Raises:
        ValueError: If no response is received from the LLM or an error occurs during the call.
    """
    logging.info(f"Verarbeite Prompt mit {len(code_file_paths)} Dateien.")
    response = call_llm(prompt)
    if not response:
        raise ValueError("Keine Antwort vom LLM erhalten oder Fehler beim Aufruf.")
    improved_code = trim_code(response.strip())
    improved_files = []
    for idx, code_file_path in enumerate(code_file_paths, start=1):
        code_file_path = (
            "/Users/jozef/PycharmProjects/PhoenixAI/phoenixai/Projects/fuego-fighters/"
            + code_file_path.split(":")[1]
        )
        improved_file = save_code_to_file(
            code_file_path, improved_code, iteration=iteration + idx
        )
        improved_files.append(improved_file)
    return improved_files


def process_issue_groups(issue_groups):
    """Processes all groups of issues.

    Args:
        issue_groups (list): A list of groups with issues."""
    for group_idx, issues_group in enumerate(issue_groups, start=1):
        logging.info(
            f"Verarbeite Gruppe {group_idx}/{len(issue_groups)} mit {len(issues_group)} Issues."
        )
        prompt = generate_group_prompt(issues_group)
        code_file_paths = [issue["component"] for issue in issues_group["issues"]]
        try:
            improved_files = process_group_with_llm(
                prompt, code_file_paths, iteration=group_idx
            )
            logging.info(
                f"Gruppe {group_idx} erfolgreich verarbeitet. Verbesserte Dateien: {improved_files}"
            )
        except Exception as e:
            logging.error(f"Fehler bei der Verarbeitung von Gruppe {group_idx}: {e}")


def process_issues_from_sonarqube():
    """Processes all SonarQube issues returned by the analysis."""
    logging.info("Starte Verarbeitung von SonarQube-Issues...")
    issues = analyze_sonar_issues()
    if not issues:
        return
    issue_groups = group_issues(issues)
    process_issue_groups(issue_groups)


if __name__ == "__main__":
    process_issues_from_sonarqube()
