# modules/analyze.py

import logging

from sonarqube import SonarQubeClient

# def start_sonarqube_instanz():
    # os.system("echo sonarqube/bin/windows-x86.64/StartSonar.bat")
    # verfy start somehow

def analyze_code():
    """
    Placeholder for code analysis functions.
    """
    # start_sonarqube_instanz()

    logging.info("Starting code analysis...")
    sonar_results = sonarqube_analysis()
    # Analysis logic goes here
    analysis_results = {
        "code_quality": None,
        "dependencies": None,
        "architecture": None,
        "sonar_issues": sonar_results['issues'],
        "test_coverage": sonar_results['coverage']
        # ...
    }
    logging.info("Code analysis completed.")
    return analysis_results

def filter_issue_data(issues):
    filtered = {}
    for issue in issues:
        filtered[issue['key']] = {
            'rule': issue['rule'],
            'component': issue['component'],
            'project': issue['project'],
            'line': issue['line'],
            'message': issue['message']
        }
    return filtered

def filter_component_tree(component_tree):
    filtered = {}
    filtered[component_tree['component']['key']] = {'coverage': component_tree['component']['measures'][0]['value']}
    return filtered

def sonarqube_analysis():
    logging.info("Starting sonarqube analysis...")
    sonarqube = SonarQubeClient(sonarqube_url="http://localhost:9000", token='squ_3d7417de160de549c708ffef8ad5b0c0dc295d00')

    print(sonarqube.auth.check_credentials())

    issues = sonarqube.issues.search_issues(componentKeys="fighter_jet", branch="main")
    filtered_issues = filter_issue_data(issues['issues'])
    print(filtered_issues)
    # print(issues)
    component_tree = sonarqube.measures.get_component_with_specified_measures(component="fighter_jet", metricKeys="coverage")
    filtered_component_tree = filter_component_tree(component_tree)
    # print(component_tree)
    print(filtered_component_tree)
    logging.info("sonarqube analysis completed!")

    return { 'issues': issues, 'coverage': filtered_component_tree}

analyze_code()