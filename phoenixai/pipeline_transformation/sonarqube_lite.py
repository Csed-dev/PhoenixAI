import logging

from phoenixai.analysis.analyze import sonarqube_analysis

from base_prompt_handling import (call_llm, generate_initial_prompt,
                                  save_code_to_file, trim_code)


def analyze_sonar_issues():
    """
    Führt eine SonarQube-Analyse durch und gibt die gefundenen Issues zurück.

    :return: Dictionary mit den Issues.
    """
    logging.info("Starte SonarQube-Analyse...")
    analysis_results = sonarqube_analysis()
    issues = analysis_results.get("issues", {})

    if not issues:
        logging.info("Keine SonarQube-Issues gefunden.")
        return None

    logging.info(f"Es wurden {len(issues)} Issues gefunden.")
    return issues


def group_issues(issues, group_size=10):
    """
    Teilt die Issues in Gruppen der angegebenen Größe auf.

    :param issues: Dictionary mit allen Issues.
    :param group_size: Anzahl der Issues pro Gruppe.
    :return: Liste von Gruppen (jeder Gruppe ist ein Dictionary von Issues).
    """
    logging.info(
        f"Teile {len(issues)} Issues in Gruppen mit jeweils {group_size} Issues."
    )
    issue_items = list(issues.items())
    return [
        dict(issue_items[i : i + group_size])
        for i in range(0, len(issue_items), group_size)
    ]


def generate_group_prompt(issues_group):
    """
    Erstellt einen gemeinsamen Prompt für eine Gruppe von Issues.

    :param issues_group: Dictionary mit einer Gruppe von Issues.
    :return: Der generierte Prompt als String.
    """
    logging.info(f"Erstelle Prompt für eine Gruppe mit {len(issues_group)} Issues.")
    prompt_parts = []
    for issue_key, issue in issues_group.items():
        prompt_parts.append(
            f"- {issue['message']} (SonarQube-Rule: {issue['rule']}) in Datei {issue['component']}."
        )

    prompt = f"{generate_initial_prompt('')}\n" + "\n".join(prompt_parts)
    return prompt


def process_group_with_llm(prompt, code_file_paths, iteration=1):
    """
    Sendet den gemeinsamen Prompt an das LLM und speichert die verbesserten Codes.

    :param prompt: Der generierte Prompt.
    :param code_file_paths: Liste der betroffenen Dateien.
    :param iteration: Iteration, um unterschiedliche Versionen zu speichern.
    :return: Liste der Pfade zu den verbesserten Dateien.
    """
    logging.info(f"Verarbeite Prompt mit {len(code_file_paths)} Dateien.")
    response = call_llm(prompt)

    if not response:
        raise ValueError("Keine Antwort vom LLM erhalten oder Fehler beim Aufruf.")

    improved_code = trim_code(response.strip())
    improved_files = []

    for idx, code_file_path in enumerate(code_file_paths, start=1):
        improved_file = save_code_to_file(
            code_file_path, improved_code, iteration=iteration + idx
        )
        improved_files.append(improved_file)

    return improved_files


def process_issue_groups(issue_groups):
    """
    Verarbeitet alle Gruppen von Issues.

    :param issue_groups: Liste von Gruppen mit Issues.
    """
    for group_idx, issues_group in enumerate(issue_groups, start=1):
        logging.info(
            f"Verarbeite Gruppe {group_idx}/{len(issue_groups)} mit {len(issues_group)} Issues."
        )
        prompt = generate_group_prompt(issues_group)
        code_file_paths = [issue["component"] for issue in issues_group.values()]

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
    """
    Verarbeitet alle SonarQube-Issues, die von der Analyse zurückgegeben werden.
    """
    logging.info("Starte Verarbeitung von SonarQube-Issues...")

    # 1. Issues analysieren
    issues = analyze_sonar_issues()
    if not issues:
        return

    # 2. Issues in Gruppen aufteilen
    issue_groups = group_issues(issues)

    # 3. Gruppen verarbeiten
    process_issue_groups(issue_groups)


# Hauptausführung
if __name__ == "__main__":
    process_issues_from_sonarqube()
