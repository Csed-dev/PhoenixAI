"""
This module provides functionality to clone a GitHub repository into a specified directory.
Functions:
- clone_repository(repo_input, clone_dir="cloned_repos"): Clones a repository from a GitHub user/repository format or a full URL into a subdirectory of clone_dir.
"""

import git
import os
import logging
from pathlib import Path
from urllib.parse import urlparse

def clone_repository(repo_input, clone_dir="cloned_repos"):
    """
    Clones a repository from a GitHub user/repository format or a full URL into a subdirectory of clone_dir.

    Parameters:
    - repo_input (str): Either the user/repository string (e.g., "user/repo") or the full repository URL.
    - clone_dir (str): Base directory where repositories will be cloned.

    Returns:
    - bool: True if cloning was successful, False otherwise.
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Determine if the input is a full URL or a "user/repo" string
    if "://" in repo_input:
        repo_url = repo_input  # Full URL provided
        parsed_url = urlparse(repo_url)
        repo_name = Path(parsed_url.path).stem  # Extract repository name from URL path
    else:
        if '/' not in repo_input:
            logging.error("Invalid repository format. Expected 'user/repo' or a full URL.")
            return False
        repo_url = f"https://github.com/{repo_input}"  # Construct GitHub URL
        repo_name = repo_input.split('/')[-1]  # Extract repository name

    # Define the target directory for the repository
    repo_dir = Path(clone_dir) / repo_name

    try:
        if not repo_dir.parent.exists():
            logging.info(f"Creating base directory: {repo_dir.parent}")
            repo_dir.parent.mkdir(parents=True, exist_ok=True)

        # Check if the repository is already cloned
        if repo_dir.exists() and any(repo_dir.iterdir()):
            logging.warning(f"Repository already cloned in: {repo_dir}. Skipping.")
            return False

        # Clone the repository
        git.Repo.clone_from(repo_url, str(repo_dir))
        logging.info(f"Repository successfully cloned into {repo_dir}")
        return True

    except git.exc.GitCommandError as git_error:
        logging.error(f"Git error: {git_error}")
    except PermissionError:
        logging.error(f"Permission denied: Unable to access or write to {repo_dir}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    
    return False

if __name__ == "__main__":
    # Example usage
    clone_repository("https://github.com/Polyfrost/OverflowAnimationsV2", "cloned_repos")