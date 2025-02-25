import os
import subprocess
import sys

# def run_command(command):
#     """Run a command and print its output in real-time."""
#     print(f"Running: {command}")
#     process = subprocess.Popen(
#         command,
#         shell=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         universal_newlines=True
#     )
   
#     for line in process.stdout:
#         print(line, end='')
   
#     process.wait()
#     if process.returncode != 0:
#         print(f"Command failed with exit code {process.returncode}")
#         return False
#     return True

def run_command(command):
    """Run a command and print its output in real-time."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # Capture STDERR as well
        universal_newlines=True
    )

    stdout, stderr = process.communicate()
    
    if stdout:
        print(stdout)
    if stderr:
        print(f"ERROR:\n{stderr}")  # Show errors

    if process.returncode != 0:
        print(f"Command failed with exit code {process.returncode}")
        sys.exit(process.returncode)  # Stop execution on failure

def main():
    # First, check what's in the current directory
    run_command('ls -la')
   
    # Create coverage config file
    with open('.coveragerc', 'w') as f:
        f.write("""[run]
source = /app
omit =
    */tests/*
    */.venv/*
    */site-packages/*
    */__pycache__/*

[html]
directory = /app/coverage_report
title = Code Coverage Report
""")
    # Debug: Ensure .coveragerc was created
    run_command('cat .coveragerc')

    # Run the coverage tests
    run_command('coverage run -m pytest -v /app/tests')
   
    # Check if .coverage exists
    run_command('ls -la /app')
   
    # Debug the coverage file
    run_command('coverage debug data')
   
    # Generate HTML report
    run_command('coverage report')
    run_command('coverage html')
    
    # Check if the report was generated
    run_command('ls -la /app/coverage_report')
   
    # Generate dependency graph
    run_command('pipdeptree --graph-output png > dependency_graph.png')
   
    print("Startup tasks completed.")

if __name__ == "__main__":
    main()