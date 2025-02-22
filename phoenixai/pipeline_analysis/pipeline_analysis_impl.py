import os
from phoenixai.pipeline_analysis.name_checker import NameChecker
from phoenixai.pipeline_analysis.performance_analysis import analyze_target, generate_report, display_report

def run_script1(file_path):
    print(f"[Analysis] Skript 1 auf: {file_path}")

def run_script2(file_path):
    print(f"[Analysis] Skript 2 auf: {file_path}")

def run_name_checker(file_path):
    print(f"[Analysis] NameChecker auf: {file_path}")
    checker = NameChecker(file_path)
    checker.generate_report()
    checker.save_report("name_checker_report.md")

def run_script4(file_path):
    print(f"[Analysis] Skript 4 auf: {file_path}")

def run_performance_analysis(file_path):
    print(f"[Analysis] Performance-Analyse auf: {file_path}")
    results = analyze_target(file_path)
    generate_report(results, "performance_report.md")
    print("Performance-Bericht wurde in 'performance_report.md' gespeichert.")
    display_report("performance_report.md", port=5000)

analysis_actions = {
    "Name Checker": run_name_checker,
    "SonarQube": run_script1,
    "Performance": run_performance_analysis,
    "Architecture": run_script4,
}
