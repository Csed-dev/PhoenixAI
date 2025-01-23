# pipeline_analysis_impl.py
import os
from phoenixai.pipeline_analysis.name_checker import NameChecker

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

analysis_actions = {
    "Name Checker": run_name_checker,
    "SonarQube": run_script1,
    "Performance": run_script2,
    "Architecture": run_script4,
    "Security": run_script4,
}

