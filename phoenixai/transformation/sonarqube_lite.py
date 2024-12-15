import json
from base_prompt_handling import generate_initial_prompt, call_llm, save_code_to_file, trim_code

def sonarqube_to_llm(issue, code_file_path, iteration=1):
    """
    Überträgt ein SonarQube-Issue in ein LLM, um Lösungen für das identifizierte Problem zu generieren.

    :param issue: Dictionary mit SonarQube-Issue-Daten (enthält z.B. 'rule', 'component', 'project', 'line', 'message').
    :param code_file_path: Pfad zur Datei, die verbessert werden soll.
    :param iteration: Iteration, um unterschiedliche Verbesserungen zu speichern.
    :return: Der Pfad zur verbesserten Datei.
    """
    # Lade den Originalcode aus der Datei
    try:
        with open(code_file_path, "r", encoding="utf-8") as f:
            original_code = f.read()
    except FileNotFoundError as e:
        raise ValueError(f"Datei nicht gefunden: {code_file_path}") from e

    # Generiere den Prompt basierend auf dem SonarQube-Issue
    prompt = f"""{generate_initial_prompt(original_code)}
    - {issue['message']} (SonarQube-Rule: {issue['rule']}).
    """

    # Anfrage an das LLM senden
    response = call_llm(prompt)

    if not response:
        raise ValueError("Keine Antwort vom LLM erhalten oder Fehler beim Aufruf.")

    # Extrahiere den reinen Code
    improved_code = response.strip()
    trimmed_code = trim_code(improved_code)

    # Code speichern
    return save_code_to_file(code_file_path, trimmed_code, iteration)


# Beispielnutzung
if __name__ == "__main__":
    # Beispiel-SonarQube-Daten
    example_issue = {
        "rule": "python:S1542",
        "component": "webscrapertest:tag_list.py",
        "project": "webscraper_test",
        "line": 1,
        "message": 'Rename function "ALL_TAGS" to match the regular expression ^[a-z][a-z0-9_]*$.'
    }

    code_path = "cloned_repos\\Py_Web_Scrape\\tag_list.py"  # Pfad zu der zu bearbeitenden Datei

    try:
        improved_file = sonarqube_to_llm(example_issue, code_path, iteration=1)
        print(f"Verbesserter Code wurde gespeichert unter: {improved_file}")
    except Exception as e:
        print(f"Fehler: {e}")
