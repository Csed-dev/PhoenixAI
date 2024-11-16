import git
import os
import logging

def clone_repository(user_repo, clone_dir="cloned_repos"):
    """
    Clones the repository from a GitHub user and repository into clone_dir.
    
    Parameters:
    - user_repo (str): The user and repository name in the format 'user/repo'.
    - clone_dir (str): Directory where the repository will be cloned.".
    """
    repo_url = f"https://github.com/{user_repo}"
    
    try:
        if not os.path.exists(clone_dir):
            os.makedirs(clone_dir)
        git.Repo.clone_from(repo_url, clone_dir)
        logging.info(f"Repository cloned into {clone_dir}")
    except Exception as e:
        logging.error(f"Failed to clone repository: {e}")
        raise