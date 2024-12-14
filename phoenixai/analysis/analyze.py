import logging
from dotenv import load_dotenv
from sonarqube_api import SonarQubeClient

load_dotenv()

sonarqube_token = os.getenv("SONARQUBE_TOKEN")
if not sonarqube_token:
    raise ValueError(
        "SONARQUBE_TOKEN nicht gesetzt. Bitte setzen Sie die Umgebungsvariable."
    )

# def start_sonarqube_instanz():
    # os.system("echo sonarqube/bin/windows-x86.64/StartSonar.bat")
    # verfy start somehow

def analyze_code():
    """
    Placeholder for code analysis functions.
    """
    # start_sonarqube_instanz()

    logging.info("Starting code analysis...")
    sonar_issues = sonarqube_analysis()
    # Analysis logic goes here
    analysis_results = {
        "code_quality": None,
        "dependencies": None,
        "architecture": None,
        "sonar_issues": sonar_issues
        # ...
    }
    logging.info("Code analysis completed.")
    return analysis_results

def sonarqube_analysis():
    logging.info("Starting sonarqube analysis...")
    # sonarqube = SonarQubeClient(sonarqube_url="http://localhost:9000", username='admin', password='admin')
    sonarqube = SonarQubeClient(sonarqube_url="http://localhost:9000", token=sonarqube_token)
    issues = sonarqube.issues.search_issues(componentKeys="webscraper_test", branch="main")
    # print(sonarqube.auth.check_credentials())
    return issues

analyze_code()