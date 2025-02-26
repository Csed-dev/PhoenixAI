###############################################################################
# MAKEFILE (phoenixai/Makefile)
###############################################################################
# We assume you run "make XXX" from: .../PhoenixAI/phoenixai
# The "Projects" folder is in the same directory as this Makefile.

# 1. Define your base Projects folder (relative to this Makefile).
BASE_DIR := Projects
BASE_DIR_W_DOT := .\Projects

# 2. Find all subfolders in the Projects folder (each subfolder is a project).
PROJECTS := $(wildcard $(BASE_DIR)/*)

# 3. Create test targets for each project
TESTS := $(foreach project, $(PROJECTS), $(addsuffix /tests, $(project)))

.PHONY: all clean debug $(TESTS) \
        pipdeptree-all-windows pipdeptree-all \
        pipdeptree-project-windows pipdeptree-project

# ------------------------------------------------------------------------------
# Default target: run all tests (for each project).
all: $(TESTS)
	@echo "Test targets completed for: $(PROJECTS)"

# ------------------------------------------------------------------------------
# 4. Test rule for each project:
#
#    - If .venv is present, ensure coverage, pytest, pipdeptree are installed
#    - Then look for test.sh, or a Makefile w/ `test` target, or test_*.py to run
#    - If found, run coverage-based tests; else skip
$(BASE_DIR)/%/tests:
	@echo "------------------------------------------------------------------------"
	@echo "[INFO] Checking for tests in project: $(@D)"
	@echo "------------------------------------------------------------------------"

	# If the local venv folder exists, ensure packages are installed.
	@if [ -d "$(@D)/.venv" ]; then \
	  echo "Ensuring pipdeptree, pytest, and coverage are installed in $(@D)"; \
	  if ! "$(@D)/.venv/Scripts/pip.exe" show pipdeptree > /dev/null 2>&1; then \
	    "$(@D)/.venv/Scripts/pip.exe" install pipdeptree; \
	  fi; \
	  if ! "$(@D)/.venv/Scripts/pip.exe" show pytest > /dev/null 2>&1; then \
	    "$(@D)/.venv/Scripts/pip.exe" install pytest; \
	  fi; \
	  if ! "$(@D)/.venv/Scripts/pip.exe" show coverage > /dev/null 2>&1; then \
	    "$(@D)/.venv/Scripts/pip.exe" install coverage; \
	  fi; \
	else \
	  echo "No .venv found in $(@D). Skipping package install checks."; \
	fi

	# 2. Run tests if any recognized method is found
	@if [ -f "$(@D)/test.sh" ]; then \
	  echo "[INFO] Found test.sh → Running it..."; \
	  cd "$(@D)" && bash test.sh; \
	elif [ -f "$(@D)/Makefile" ] && grep -q "^test:" "$(@D)/Makefile"; then \
	  echo "[INFO] Found Makefile with 'test' target → make test"; \
	  cd "$(@D)" && make test; \
	elif find "$(@D)" -maxdepth 1 -type f -name "test_*.py" | grep -q "." || \
	     find "$(@D)" -maxdepth 1 -type f -name "tests_*.py" | grep -q "."; then \
	  if [ -f "$(@D)/.venv/Scripts/python.exe" ]; then \
	    echo "[INFO] Found Python test files → Running coverage+pytest"; \
	    cd "$(@D)" && .venv/Scripts/python.exe -m coverage run -m pytest; \
	    cd "$(@D)" && .venv/Scripts/python.exe -m coverage report; \
	  else \
	    echo "[WARNING] No local python.exe to run tests. Skipping..."; \
	  fi; \
	else \
	  echo "[INFO] No recognized test system. Skipping tests in $(@D)."; \
	fi

# ------------------------------------------------------------------------------
# 5. pipdeptree-all-windows
#    - Runs the PowerShell script for ALL projects on Windows
pipdeptree-all-windows:
	powershell -File "./generate_pipdeptree_all.ps1" -BaseDir "$(BASE_DIR_W_DOT)"

# ------------------------------------------------------------------------------
# 6. pipdeptree-all
#    - (Optional) If you want a purely Bash-based approach for all projects:
pipdeptree-all:
	@for project in $(PROJECTS); do \
	  echo "**********************************************************"; \
	  echo "[INFO] Processing $$project..."; \
	  if [ -d "$$project/.venv" ]; then \
	    # Ensure packages
	    if ! "$$project/.venv/Scripts/pip.exe" show pipdeptree > /dev/null 2>&1; then \
	      "$$project/.venv/Scripts/pip.exe" install pipdeptree; \
	    fi; \
	    if ! "$$project/.venv/Scripts/pip.exe" show pytest > /dev/null 2>&1; then \
	      "$$project/.venv/Scripts/pip.exe" install pytest; \
	    fi; \
	    if ! "$$project/.venv/Scripts/pip.exe" show coverage > /dev/null 2>&1; then \
	      "$$project/.venv/Scripts/pip.exe" install coverage; \
	    fi; \
	  fi; \
	  # Run coverage-based tests if found
	  if [ -f "$$project/test.sh" ]; then \
	    echo "[INFO] Running $$project test.sh..."; \
	    cd $$project && bash test.sh; \
	  elif [ -f "$$project/Makefile" ] && grep -q "^test:" "$$project/Makefile"; then \
	    echo "[INFO] Running $$project make test..."; \
	    cd $$project && make test; \
	  elif find "$$project" -maxdepth 1 -type f -name "test_*.py" | grep -q "." || \
	       find "$$project" -maxdepth 1 -type f -name "tests_*.py" | grep -q "."; then \
	    if [ -f "$$project/.venv/Scripts/python.exe" ]; then \
	      echo "[INFO] Running coverage+pytest in $$project..."; \
	      cd $$project && .venv/Scripts/python.exe -m coverage run -m pytest; \
	      cd $$project && .venv/Scripts/python.exe -m coverage report; \
	    fi; \
	  fi; \
	  # Ensure requirements.txt
	  if [ ! -f "$$project/requirements.txt" ] && [ -f "$$project/.venv/Scripts/pip.exe" ]; then \
	    echo "[INFO] Generating requirements.txt in $$project..."; \
	    cd $$project && .venv/Scripts/pip.exe list --format=freeze > requirements.txt; \
	  fi; \
	  # Generate dependencies.svg
	  if [ -f "$$project/.venv/Scripts/python.exe" ]; then \
	    echo "[INFO] Generating pipdeptree → dependencies.svg in $$project..."; \
	    cd $$project && .venv/Scripts/python.exe -m pipdeptree --graph-output svg > dependencies.svg; \
	  else \
	    echo "[WARNING] No local python.exe found in $$project. Skipping pipdeptree..."; \
	  fi; \
	done

# ------------------------------------------------------------------------------
# 7. pipdeptree-project-windows
#    - Provide PROJECT=<foldername> to run coverage/tests & pipdeptree on Windows
pipdeptree-project-windows:
	@powershell -Command " \
		if (!('$(PROJECT)' -ne '')) { \
			Write-Error 'Error: You must specify PROJECT=ProjectName'; \
			exit 1; \
		} \
		Write-Host 'Processing single project: $(PROJECT)'; \
		& powershell -File './generate_pipdeptree_all.ps1' -BaseDir '$(BASE_DIR_W_DOT)' -SingleProject '$(PROJECT)'; \
	"

# ------------------------------------------------------------------------------
# 8. pipdeptree-project (optional Bash version)
pipdeptree-project:
	@if [ -z "$(PROJECT)" ]; then \
		echo "Error: You must specify PROJECT=ProjectName"; \
		exit 1; \
	fi
	@if [ ! -d "$(BASE_DIR)/$(PROJECT)" ]; then \
		echo "Error: Project '$(PROJECT)' does not exist in '$(BASE_DIR)'."; \
		exit 1; \
	fi
	@echo "Processing single project: $(BASE_DIR)/$(PROJECT)"
	# (Replicate the same steps as the all-in-one approach above)
	@if [ -d "$(BASE_DIR)/$(PROJECT)/.venv" ]; then \
	  # ensure packages
	  if ! "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/pip.exe" show pipdeptree > /dev/null 2>&1; then \
	    "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/pip.exe" install pipdeptree; \
	  fi; \
	  if ! "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/pip.exe" show pytest > /dev/null 2>&1; then \
	    "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/pip.exe" install pytest; \
	  fi; \
	  if ! "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/pip.exe" show coverage > /dev/null 2>&1; then \
	    "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/pip.exe" install coverage; \
	  fi; \
	fi
	# run tests
	@if [ -f "$(BASE_DIR)/$(PROJECT)/test.sh" ]; then \
	  echo "[INFO] Running test.sh..."; \
	  cd "$(BASE_DIR)/$(PROJECT)" && bash test.sh; \
	elif [ -f "$(BASE_DIR)/$(PROJECT)/Makefile" ] && grep -q "^test:" "$(BASE_DIR)/$(PROJECT)/Makefile"; then \
	  echo "[INFO] Running make test..."; \
	  cd "$(BASE_DIR)/$(PROJECT)" && make test; \
	elif find "$(BASE_DIR)/$(PROJECT)" -maxdepth 1 -type f -name "test_*.py" | grep -q "." || \
	     find "$(BASE_DIR)/$(PROJECT)" -maxdepth 1 -type f -name "tests_*.py" | grep -q "."; then \
	  if [ -f "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/python.exe" ]; then \
	    cd "$(BASE_DIR)/$(PROJECT)" && .venv/Scripts/python.exe -m coverage run -m pytest; \
	    cd "$(BASE_DIR)/$(PROJECT)" && .venv/Scripts/python.exe -m coverage report; \
	  fi; \
	else \
	  echo "[INFO] No recognized tests in $(PROJECT)."; \
	fi
	# ensure requirements & pipdeptree
	@if [ ! -f "$(BASE_DIR)/$(PROJECT)/requirements.txt" ] && [ -f "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/pip.exe" ]; then \
	  echo "[INFO] Creating requirements.txt..."; \
	  cd "$(BASE_DIR)/$(PROJECT)" && .venv/Scripts/pip.exe list --format=freeze > requirements.txt; \
	fi
	@if [ -f "$(BASE_DIR)/$(PROJECT)/.venv/Scripts/python.exe" ]; then \
	  echo "[INFO] Generating dependencies.svg..."; \
	  cd "$(BASE_DIR)/$(PROJECT)" && .venv/Scripts/python.exe -m pipdeptree --graph-output svg > dependencies.svg; \
	else \
	  echo "[WARNING] No local python.exe found in $(PROJECT). Skipping pipdeptree..."; \
	fi

# ------------------------------------------------------------------------------
# 9. clean
clean:
	@echo "[INFO] Cleaning up projects..."
	@for project in $(PROJECTS); do \
		echo "------------------------------------------------------------"; \
		echo "[INFO] Cleaning $$project..."; \
		if [ -f "$$project/clean.sh" ]; then \
			cd "$$project" && bash clean.sh; \
		else \
			find "$$project" -type d -name "__pycache__" -exec rm -rf {} +; \
			find "$$project" -type f -name "*.pyc" -delete; \
		fi; \
	done

# ------------------------------------------------------------------------------
# Debug info
debug:
	@echo "BASE_DIR:          $(BASE_DIR)"
	@echo "BASE_DIR_W_DOT:    $(BASE_DIR_W_DOT)"
	@echo "PROJECTS:          $(PROJECTS)"
	@echo "TESTS (for 'all'): $(TESTS)"
