import logging
from modules import clone_repo, analyze, transform, cicd, feedback_loop

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Configuration
    repo_url = "https://github.com/legacy/codebase.git"
    clone_dir = "cloned_repos/legacy_codebase"

    # Step 1: Clone the Repository
    clone_repo.clone_repository(repo_url, clone_dir)

    # Step 2: Analyze the Code
    analysis_results = analyze.analyze_code(clone_dir)

    # Step 3: Transform the Code using LLM
    transformed_code_path = transform.transform_code(analysis_results)

    # Step 4: Push and Test
    cicd.trigger_cicd_pipeline()
    test_results = cicd.get_test_results()

    # Step 5: Iterative Improvement
    feedback_loop.iterative_improvement(test_results)

if __name__ == "__main__":
    main()
